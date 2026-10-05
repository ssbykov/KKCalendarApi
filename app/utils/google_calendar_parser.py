import asyncio
import html
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.core import settings
from app.database import SessionDep, db_helper
from app.database.crud.days_info import DayInfoRepository
from app.database.crud.elements import ElementsRepository
from app.database.crud.events import EventRepository
from app.database.crud.haircutting_days import HaircuttingRepository
from app.database.crud.la_positions import LaPositionRepository
from app.database.crud.skylight_arches import SkylightArchRepository
from app.database.crud.users import UsersRepository
from app.database.crud.yelams import YelamRepository
from app.database.schemas import DayInfoSchemaCreate, EventSchemaCreate
from app.utils.translator import translate

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


@dataclass
class ParsedDay:
    moon: int
    moon_day: int
    elements: tuple[str, str]
    events: list[dict[str, str]]


class GoogleCalendarParser:
    HOST = "https://www.karmakagyucalendar.org/current-calendar"
    MONTHS_TAG = "CjVfdc"
    DAY_TAG = "n8H08c UVNKR"
    URL_PATTERN = r"➡️ [^\s]+|🌐 [^\s]+|https?://[^\s]+"

    FILTER_WORDS_IN_EVENTS = (
        "🌑",
        "🌕",
        "100x",
        "1000x",
        "1,000x",
        "10000x",
        "10,000x",
        "100000x",
        "1000000x",
        "10000000x",
        "100,000x",
        "10,000,000x",
    )

    DUCHEN_EVENTS = {
        "Chötrül Düchen",
        "Saga Dawa Düchen",
        "Chökhor Düchen",
        "Lha Bab Düchen",
    }

    BLOCK_SPLIT_RE = re.compile(r"<br\s*/?>\s*<br\s*/?>", re.I)
    BR_RE = re.compile(r"<br\s*/?>", re.I)
    TAG_RE = re.compile(r"<[^>]+>")
    LINK_BLOCK_RE = re.compile(
        r'^\s*<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>(.*)$', re.I | re.S
    )
    BOLD_BLOCK_RE = re.compile(r"^\s*<b>(.*?)</b>(.*)$", re.I | re.S)
    DATE_RE = re.compile(r"^(\d{1,2})\s*\.\s*(\d{1,2})\.?$")
    HEADER_SPLIT_RE = re.compile(r"\s*[⋅·]\s*")
    ELEMENTS_RE = re.compile(r"\(\s*([A-Za-z]+)\s*-\s*([A-Za-z]+)\s*\)")
    NOISE_RE = re.compile(r"^[\d,\s]+(x|times)(\s+day)?$", re.I)
    STOP_PREFIXES = ("ELEMENTAL COMBINATION", "-----", "THE KARMA KAGYU")

    def __init__(self, session: SessionDep):
        self.calendar_id = settings.calendar.calendar_id
        with open(settings.calendar.secret_file, "r", encoding="utf-8") as f:
            account_info = json.load(f)
        self.creds = service_account.Credentials.from_service_account_info(
            account_info, scopes=SCOPES
        )  # type: ignore
        self.service = build("calendar", "v3", credentials=self.creds)
        self.session = session
        self.day_info_repo = DayInfoRepository(self.session)
        self.event_repo = EventRepository(self.session)
        self._elements = None  # Кеш справочника элементов
        self._archs = None
        self._las = None
        self._haircuttings = None
        self._yelams = None
        self._events = None

    async def initialize_caches(self):
        elements_repo = ElementsRepository(self.session)
        arch_repo = SkylightArchRepository(self.session)
        la_repo = LaPositionRepository(self.session)
        haircutting_repo = HaircuttingRepository(self.session)
        yelam_repo = YelamRepository(self.session)

        self._events = await self.event_repo.get_all_dict()
        self._elements = await elements_repo.get_all_dict()
        self._archs = await arch_repo.get_all_dict()
        self._las = await la_repo.get_all_dict()
        self._haircuttings = await haircutting_repo.get_all_dict()
        self._yelams = await yelam_repo.get_all_dict()

    async def load_events(
        self, year: int, month: int, period: int, update: bool
    ) -> dict[str, list[str]]:
        calendar_days_info = await self._calendar_request(year, month, period)
        user_repo = UsersRepository(self.session)
        user_id = await user_repo.get_user_id(settings.super_user.email)
        days_info = []
        new_events: set[str] = set()

        for day in calendar_days_info:
            try:
                parsed = self._parse_description(day.get("description", ""))
                elements_id = self._resolve_elements_id(parsed.elements)
                processed, new, _ = await self._handle_events(
                    parsed_events=parsed.events, user_id=user_id, update=update
                )
                day_info = self._build_day_info(parsed, day, elements_id, processed)
            except Exception:
                logging.exception(
                    "Ошибка обработки дня %s (%s)", day.get("id"), day.get("summary")
                )
                continue
            new_events |= new
            days_info.append(day_info)

        if calendar_days_info and not days_info:
            raise RuntimeError(
                f"Ни один из {len(calendar_days_info)} дней не разобран, "
                "смотрите ошибки выше"
            )

        result = await self.day_info_repo.add_days(days_info, update)
        if new_events:
            result["New events"] = list(new_events)
        return result

    async def _calendar_request(
        self, year: int, month: int, period: int = 1
    ) -> list[dict[str, Any]]:
        start_of_month = (
            datetime(year, month, 1).isoformat() + "Z"
        )  # 'Z' указывает на время UTC
        new_month = (month + period - 1) % 12 + 1
        add_year = (month + period - 1) // 12
        end_of_month = datetime(year + add_year, new_month, 1).isoformat() + "Z"

        try:
            days_info_result = (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=start_of_month,
                    timeMax=end_of_month,
                    singleEvents=True,
                    orderBy="startTime",
                    maxResults=2500,
                )
                .execute()
            )
            return days_info_result.get("items", [])  # type: ignore
        except Exception as error:
            logging.error(f"An error occurred: {error}")
            return []

    # ------------------------------------------------------------------
    # Разбор description
    # ------------------------------------------------------------------

    @classmethod
    def _html_to_text(cls, fragment: str) -> str:
        text = cls.BR_RE.sub("\n", fragment)
        return html.unescape(cls.TAG_RE.sub("", text)).strip()

    @staticmethod
    def _clean_name(s: str) -> str:
        # только нормализация пробелов; звёздочки сохраняются
        return re.sub(r"\s+", " ", s).strip()

    @classmethod
    def _is_noise(cls, name: str) -> bool:
        return (
                not name
                or name in cls.FILTER_WORDS_IN_EVENTS
                or bool(cls.NOISE_RE.match(name))
        )

    @staticmethod
    def _norm(s: str) -> str:
        # только пробелы и регистр; X, X* и X** остаются разными событиями
        return re.sub(r"\s+", " ", s).strip().casefold()

    def _parse_description(self, description: str) -> ParsedDay:
        blocks = [
            b.strip() for b in self.BLOCK_SPLIT_RE.split(description) if b.strip()
        ]
        if not blocks:
            raise ValueError("Пустое описание")

        # Заголовок: дата · события · стихии · служебные поля
        parts = [
            p.strip()
            for p in self.HEADER_SPLIT_RE.split(self._html_to_text(blocks[0]))
            if p.strip()
        ]
        m = self.DATE_RE.match(parts[0]) if parts else None
        if not m:
            raise ValueError(f"Не удалось разобрать дату: {parts[:1]}")
        moon, moon_day = int(m[1]), int(m[2])

        el_idx, elements = None, None
        for i, p in enumerate(parts[1:], 1):
            if em := self.ELEMENTS_RE.search(p):
                el_idx, elements = i, (em[1].capitalize(), em[2].capitalize())
                break
        if elements is None or el_idx is None:
            raise ValueError(f"Стихии не найдены в заголовке: {parts}")

        head_names = [self._clean_name(p) for p in parts[1:el_idx]]

        # Блоки событий до ELEMENTAL COMBINATION
        body: list[dict[str, str]] = []
        for block in blocks[1:]:
            plain = self._html_to_text(block)
            if plain.startswith(self.STOP_PREFIXES):
                break
            if lm := self.LINK_BLOCK_RE.match(block):
                link, name_html, rest = lm.groups()
            elif bm := self.BOLD_BLOCK_RE.match(block):
                link, (name_html, rest) = "", bm.groups()
            else:
                # блок без названия: продолжение текста предыдущего события
                if body:
                    body[-1]["text"] = (body[-1]["text"] + "\n" + plain).strip()
                continue

            rest_text = self._html_to_text(rest)
            stars = re.match(r"\**", rest_text).group(0)  # '*', '**' или ''
            body.append(
                {
                    "name": self._clean_name(self._html_to_text(name_html)) + stars,
                    "text": rest_text[len(stars):].lstrip(". ").strip(),
                    "link": link,
                }
            )

        # Сопоставление событий заголовка с блоками тела: только точное
        used: set[int] = set()
        events: list[dict[str, str]] = []
        for name in head_names:
            if self._is_noise(name):
                continue
            key = self._norm(name)
            found = next(
                (
                    i
                    for i, b in enumerate(body)
                    if i not in used and self._norm(b["name"]) == key
                ),
                None,
            )
            if found is None:
                events.append({"name": name, "text": "", "link": ""})
            else:
                used.add(found)
                b = body[found]
                events.append({"name": name, "text": b["text"], "link": b["link"]})

        # Блоки тела, которых нет в заголовке
        for i, b in enumerate(body):
            if i not in used and not self._is_noise(b["name"]):
                events.append(dict(b))

        self._parse_links([e for e in events if not e["link"]])
        return ParsedDay(moon, moon_day, elements, events)

    def _resolve_elements_id(self, elements: tuple[str, str]) -> int:
        el1, el2 = elements
        elements_id = self._elements.get(f"{el1}-{el2}") or self._elements.get(
            f"{el2}-{el1}"
        )
        if elements_id is None:
            raise ValueError(f"Комбинации стихий нет в справочнике: {el1}-{el2}")
        return elements_id

    def _build_day_info(
        self,
        parsed: ParsedDay,
        day: dict[str, Any],
        elements_id: int,
        events: list[int],
    ) -> DayInfoSchemaCreate:
        moon, moon_day = parsed.moon, parsed.moon_day
        return DayInfoSchemaCreate(
            date=day.get("start", {}).get("date", ""),
            moon_day=f"{moon_day}.{moon}",
            elements_id=elements_id,
            arch_id=self._archs.get(moon_day % 10),
            la_id=self._las.get(moon_day),
            haircutting_id=self._haircuttings.get(moon_day),
            yelam_id=self._yelams.get(moon),
            events=events,
        )

    # ------------------------------------------------------------------
    # События
    # ------------------------------------------------------------------

    async def _handle_events(
        self, parsed_events: list[dict[str, str]], user_id: int, update: bool
    ) -> tuple[list[int], set[str], dict[int, str]]:
        processed_event_ids = []
        new_events = set()
        events_for_translate = {}

        for event in parsed_events:
            event_name = next(
                (d for d in self.DUCHEN_EVENTS if d in event["name"]), event["name"]
            )
            event["name"] = event_name
            if existing_id := self._events.get(event_name):
                processed_event_ids.append(existing_id)
            else:
                new_events.add(event_name)
                ru_text = (
                    await asyncio.to_thread(translate, event["text"])
                    if event["text"]
                    else ""
                )
                schema = EventSchemaCreate(
                    name=event_name,
                    en_name=event_name,
                    en_text=event["text"],
                    ru_name=event_name,
                    ru_text=ru_text,
                    link=event["link"],
                    user_id=user_id,
                )
                if update:
                    new_id = await self.event_repo.add_event(schema)
                    events_for_translate[new_id] = event_name
                else:
                    new_id = -1
                processed_event_ids.append(new_id)
                self._events[event_name] = new_id

        return processed_event_ids, new_events, events_for_translate

    def _parse_links(self, events: list[dict[str, str]]) -> list[dict[str, str]]:
        for event in events:
            if not (text := event.get("text")):
                continue

            lines = text.split("\n")
            if matches := re.findall(self.URL_PATTERN, text):
                last_match = matches[-1]
                if last_match in lines[-1]:
                    lines.pop(-1)
                last_match = last_match.strip(r"➡️ 🌐")
                if not last_match.startswith("http"):
                    last_match = "http://" + last_match
                event["link"] = last_match

            cleaned_text = "\n".join(line for line in lines if line.strip())
            event["text"] = cleaned_text

        return events


async def calendar_parser_run(
    period: int, update: bool = False
) -> dict[str, list[str]] | None:
    async for session in db_helper.get_session():
        parser = GoogleCalendarParser(session)
        await parser.initialize_caches()
        today = datetime.now()
        result = await parser.load_events(
            year=today.year,
            month=today.month,
            period=period,
            update=update,
        )
        return result
    return None
