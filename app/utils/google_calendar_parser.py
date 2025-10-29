import json
import logging
import re
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
        "10000x",
        "100000x",
        "1000000x",
        "10000000x",
        "10,000,000x",
    )
    FILTER_WORDS_OUT_EVENTS = (
        "Yelam",
        "haircutting day",
        "LA:",
        "): Do",
        "): No",
    )

    DUCHEN_EVENTS = {
        "Chötrül Düchen",
        "Saga Dawa Düchen",
        "Chökhor Düchen",
        "Lha Bab Düchen",
    }

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
        events_for_translate = {}
        new_events = set()
        for day in calendar_days_info:
            summary = day.get("summary", "").split(" ⋅ ")
            descriptions = day.get("description", "").split("\n\n")

            for item in reversed(summary):
                if "haircutting day" not in item:
                    last = summary.pop()
                    summary.insert(1, last)
                else:
                    break

            new_summary = [
                event
                for event in summary
                if all([word not in event for word in self.FILTER_WORDS_OUT_EVENTS])
            ]

            head_events = new_summary[1:-1].copy()
            body_events = self._extract_body_events(descriptions)
            parsed_events = self._events_filter(head_events, body_events)

            processed, new, to_translate = await self._handle_events(
                parsed_events=parsed_events, user_id=user_id, update=update
            )
            events_for_translate.update(to_translate)
            new_events |= new

            day_info = await self._build_day_info(
                summary=new_summary,
                day=day,
                events=processed,
            )
            days_info.append(day_info)

        if events_for_translate:
            translated_events = translate(
                "|".join(events_for_translate.values())
            ).split("|")
            for event_id, ru_name in zip(
                events_for_translate.keys(), translated_events
            ):
                await self.event_repo.ru_name_event_update(event_id, ru_name)

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

    @staticmethod
    def _extract_body_events(descriptions: list[str]) -> list[str]:
        body_events = []
        for index, value in enumerate(descriptions):
            if "ELEMENTAL COMBINATION" in value:
                body_events.extend(descriptions[:index])
                break
        return body_events

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
                ru_text = translate(event["text"]) if event["text"] else ""
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

    async def _build_day_info(
        self, summary: list[str], day: dict[str, Any], events: list[int]
    ) -> DayInfoSchemaCreate:
        moon, moon_day = map(int, summary[0].strip(".").split("."))

        el1, el2 = summary[-1].split("-")
        elements_id = self._elements.get(f"{el1}-{el2}") or self._elements.get(
            f"{el2}-{el1}"
        )
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

    def _events_filter(
        self, head_events: list[str], body_events: list[str]
    ) -> list[dict[str, str]]:
        events: list[dict[str, str]] = []
        buffer_body_events = body_events.copy()
        len_body_events = len(body_events)
        for head_event in head_events:
            if head_event not in self.FILTER_WORDS_IN_EVENTS:
                event = {"name": head_event, "text": "", "link": ""}
                for idx, body_event in enumerate(body_events):
                    if head_event in body_event:
                        if body_event.startswith(head_event):
                            event["text"] = (
                                body_event.lstrip(head_event).lstrip(".:").strip()
                            )
                        else:
                            event["text"] = body_event
                        ext_events = []
                        if buffer_idx := buffer_body_events.index(body_event):
                            if events:
                                ext_events = buffer_body_events[:buffer_idx]
                                events[-1]["text"] += "\n" + "\n".join(ext_events)
                        buffer_body_events = body_events.copy()[idx + 1 :]
                        for ext_event in ext_events:
                            body_events.remove(ext_event)
                        body_events.remove(body_event)
                        break
                events.append(event)

        if buffer_body_events and len(buffer_body_events) != len_body_events:
            if events:
                events[-1]["text"] += "\n" + "\n".join(buffer_body_events)
                for buffer_body_event in buffer_body_events:
                    body_events.remove(buffer_body_event)

        for body_event in body_events:
            events.append({"name": body_event, "text": "", "link": ""})

        return self._parse_links(events)

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
