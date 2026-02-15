import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

# Предполагается, что ваши существующие импорты и настройки остаются
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


class KarmakagyuCalendarParser:
    """
    Парсер для сайта https://www.karmakagyucalendar.org/current-calendar
    Извлекает данные из HTML страницы.
    """

    BASE_URL = "https://www.karmakagyucalendar.org"
    CURRENT_CALENDAR_PATH = "/current-calendar"

    # Регулярные выражения и фильтры (можно адаптировать из старого кода)
    URL_PATTERN = r"➡️ [^\s]+|🌐 [^\s]+|https?://[^\s]+"
    FILTER_WORDS_IN_EVENTS = (
        "🌑",
        "🌕",
        "100 times day",
        "100,000 times day",
        "10,000,000 times day",
        # "100000x",
        # "1000000x",
        # "10000000x",
        # "10,000,000x",
    )
    FILTER_WORDS_OUT_EVENTS = (
        "Yelam",
        "haircutting day",
        "LA:",
        ": Do no",
        ": No memorial",
    )
    DUCHEN_EVENTS = {
        "Chötrül Düchen",
        "Saga Dawa Düchen",
        "Chökhor Düchen",
        "Lha Bab Düchen",
    }

    def __init__(self, session: SessionDep):
        self.session = session
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

        # Репозитории (как в старом коде)
        self.day_info_repo = DayInfoRepository(self.session)
        self.event_repo = EventRepository(self.session)

        # Кеши справочников
        self._elements: Dict[str, int] = {}
        self._archs: Dict[int, int] = {}
        self._las: Dict[int, int] = {}
        self._haircuttings: Dict[int, int] = {}
        self._yelams: Dict[int, int] = {}
        self._events: Dict[str, int] = {}

    async def initialize_caches(self):
        """Инициализация кешей из БД (как в старом коде)"""
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

    async def close(self):
        """Закрытие HTTP клиента"""
        await self.client.aclose()

    async def fetch_page(self) -> Optional[str]:
        """Загрузка HTML страницы"""
        url = urljoin(self.BASE_URL, self.CURRENT_CALENDAR_PATH)
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            logging.error(f"HTTP error while fetching {url}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error while fetching {url}: {e}")
            return None

    def parse_months_data(self, html: str) -> List[Dict[str, Any]]:
        """
        Парсит HTML и группирует дни по месяцам, используя поиск предшествующего заголовка.
        """
        soup = BeautifulSoup(html, "html.parser")

        # 1. Находим все заголовки месяцев (h1 с классом duRjpb, содержащие месяц и год)
        month_headers = []
        for header in soup.find_all("h1", class_=lambda c: c and "duRjpb" in c):
            text = header.get_text().strip()
            match = re.search(
                r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
                text,
                re.IGNORECASE,
            )
            if match:
                month_name = match.group(1)
                year = int(match.group(2))
                month_num = datetime.strptime(month_name, "%B").month
                month_headers.append(
                    {
                        "element": header,
                        "month_name": month_name,
                        "year": year,
                        "month": month_num,
                        "days": [],
                    }
                )

        if not month_headers:
            logging.warning("Не найдены заголовки месяцев на странице")
            return []

        # 2. Находим все параграфы дней (p с классом zfr3Q)
        day_paragraphs = soup.find_all("p", class_=lambda c: c and "zfr3Q" in c)

        # 3. Для каждого параграфа определяем месяц по ближайшему предшествующему заголовку
        for p in day_paragraphs:
            day_text = p.get_text(" ", strip=True)
            # Проверяем, что это действительно строка дня (исправленное регулярное выражение)
            if not self._is_day_line(day_text):
                continue

            # Ищем предшествующий заголовок месяца
            prev_header_elem = p.find_previous(
                "h1", class_=lambda c: c and "duRjpb" in c
            )
            if not prev_header_elem:
                continue

            # Находим соответствующий объект в month_headers
            month_info = next(
                (h for h in month_headers if h["element"] is prev_header_elem), None
            )
            if not month_info:
                continue

            # Парсим содержимое дня
            parsed_day = self._parse_day_line(
                day_text, month=month_info["month"], year=month_info["year"]
            )
            if parsed_day:
                month_info["days"].append(parsed_day)

        # 4. Формируем итоговый список (только месяцы с днями)
        months_data = [
            {
                "month_name": h["month_name"],
                "year": h["year"],
                "month": h["month"],
                "days": h["days"],
            }
            for h in month_headers
            if h["days"]
        ]

        # # Логируем результат
        # for m in months_data:
        #     logging.info(
        #         f"Месяц {m['month_name']} {m['year']}: найдено {len(m['days'])} дней"
        #     )

        return months_data

    @staticmethod
    def _is_day_line(text: str) -> bool:
        """Проверяет, является ли текст строкой описания дня."""
        # Формат: цифра(ы), пробел, слово (день недели), затем необязательные пробелы и двоеточие
        return bool(re.match(r"^\d+\s+[A-Za-z]+\s*:", text))

    def _parse_day_line(
        self, line: str, month: int, year: int
    ) -> Optional[Dict[str, Any]]:
        """
        Парсинг одной строки, описывающей день.
        Возвращает словарь с данными дня.
        """
        data = {
            "date": None,
            "lunar_day": None,
            "moon_day": None,
            "moon_month_num": None,
            "events": [],
            "elements": None,
            "arch": None,
            "la": None,
            "yelam": None,
            "haircutting": None,
        }

        # Разделяем по разделителю ⋅
        parts = [p.strip() for p in line.split("⋅")]
        if len(parts) < 3:
            return None

        # Первая часть: "1 Sunday: 12.15." или "7 Saturday : 12.21."
        first_part = parts[0]
        # Извлекаем западное число и лунную дату
        # Теперь допускаем пробелы перед двоеточием
        match = re.match(r"(\d+)\s+[A-Za-z]+\s*:\s*(\d+)\.(\d+)\.", first_part)
        if match:
            day_of_month = int(match.group(1))
            moon_day_num = int(match.group(3))
            moon_month_num = int(match.group(2))
            data["date"] = datetime(year, month, day_of_month).date()
            data["lunar_day"] = f"{moon_day_num}.{moon_month_num}"
            data["moon_day"] = moon_day_num
            data["moon_month_num"] = moon_month_num

        # Проходим по остальным частям и определяем тип информации
        for part in parts[1:]:
            part = part.strip()
            if not part:
                continue

            # Элементы (Fire-Fire, Water-Earth...)
            if re.match(r"^(Fire|Water|Earth|Wind)-", part):
                data["elements"] = part

            # Положение ЛА
            elif part.startswith("LA:"):
                data["la"] = part.replace("LA:", "").strip()

            # Направление Елам
            elif part.startswith("Yelam:"):
                data["yelam"] = part.replace("Yelam:", "").strip()

            # Дни стрижек
            elif "haircutting day" in part.lower():
                data["haircutting"] = part

            # Небесные арки (Nyen, Tshong...)
            elif any(
                arch in part
                for arch in [
                    "NYEN:",
                    "TSHONG:",
                    "MAG:",
                    "DUR:",
                    "PAG:",
                    "PU:",
                    "KHAR:",
                    "DÖN:",
                    "SI:",
                    "CSI:",
                ]
            ):
                data["arch"] = part

            # Всё остальное - события (возможно со ссылками)
            elif part not in self.FILTER_WORDS_IN_EVENTS:
                # Извлекаем ссылки из текста события
                link = self._extract_link(part)
                event_data = {"name": part, "text": "", "link": link}
                if link:
                    # Убираем ссылку из названия
                    event_data["name"] = re.sub(self.URL_PATTERN, "", part).strip()
                data["events"].append(event_data)

        return data

    def _extract_link(self, text: str) -> str:
        """Извлечение ссылки из текста события"""
        if matches := re.findall(self.URL_PATTERN, text):
            last_match = matches[-1]
            last_match = last_match.strip(r"➡️ 🌐")
            if not last_match.startswith("http"):
                last_match = "http://" + last_match
            return last_match
        return ""

    async def process_day_data(
        self, day_data: Dict[str, Any], user_id: int, update: bool
    ) -> Optional[DayInfoSchemaCreate]:
        """
        Преобразование распарсенных данных в схему БД с использованием справочников.
        """
        # Получаем ID элементов из кешей
        elements_id = None
        if day_data.get("elements"):
            elements = day_data.get("elements").split("-")
            elements_id = self._elements.get(
                day_data["elements"]
            ) or self._elements.get(f"{elements[1]}-{elements[0]}")

        arch_id = None
        if day_data.get("arch"):
            arch_id = self._archs.get(day_data.get("moon_day", 0) % 10)

        la_id = None
        if day_data.get("la"):
            la_id = self._las.get(day_data.get("moon_day", 0))

        haircutting_id = None
        if day_data.get("haircutting"):
            # Определяем тип дня стрижки (Auspicious/Inauspicious)
            haircutting_id = self._haircuttings.get(day_data.get("moon_day", 0))

        yelam_id = None
        if day_data.get("yelam"):
            yelam_id = self._yelams.get(
                day_data.get("moon_month_num", 0)
            )  # Или по месяцу?

        # Обрабатываем события
        event_ids = []
        for event_data in day_data.get("events", []):
            event_name = event_data["name"]
            # Проверяем, есть ли уже такое событие в кеше
            if existing_id := self._events.get(event_name):
                event_ids.append(existing_id)
            else:
                # Создаем новое событие
                ru_text = translate(event_data["text"]) if event_data["text"] else ""
                schema = EventSchemaCreate(
                    name=event_name,
                    en_name=event_name,
                    en_text=event_data["text"],
                    ru_name=event_name,
                    ru_text=ru_text,
                    link=event_data["link"],
                    user_id=user_id,
                )
                if update:
                    new_id = await self.event_repo.add_event(schema)
                    self._events[event_name] = new_id
                    event_ids.append(new_id)
                else:
                    event_ids.append(
                        -1
                    )  # Плейсхолдер для новых событий в режиме без обновления

        return DayInfoSchemaCreate(
            date=day_data["date"].strftime("%Y-%m-%d"),
            moon_day=day_data["lunar_day"],
            elements_id=elements_id,
            arch_id=arch_id,
            la_id=la_id,
            haircutting_id=haircutting_id,
            yelam_id=yelam_id,
            events=event_ids,
        )

    async def load_events(self, update: bool = False) -> Dict[str, List[str]]:
        """
        Основной метод загрузки и обработки данных.
        """
        html = await self.fetch_page()
        if not html:
            return {"error": ["Не удалось загрузить страницу"]}

        months_data = self.parse_months_data(html)

        user_repo = UsersRepository(self.session)
        user_id = await user_repo.get_user_id(settings.super_user.email)

        all_days_info = []
        new_events = set()

        for month_data in months_data:
            for day_data in month_data["days"]:
                try:
                    day_schema = await self.process_day_data(day_data, user_id, update)
                    if day_schema:
                        all_days_info.append(day_schema)
                except Exception as e:
                    logging.error(f"Ошибка обработки дня {day_data.get('date')}: {e}")
                    continue

        # Сохраняем дни в БД
        result = await self.day_info_repo.add_days(all_days_info, update)

        if new_events:
            result["New events"] = list(new_events)

        return result


async def calendar_parser_run(update: bool = False) -> Dict[str, List[str]] | None:
    """
    Функция для запуска парсера из внешнего кода.
    """
    async for session in db_helper.get_session():
        parser = KarmakagyuCalendarParser(session)
        try:
            await parser.initialize_caches()
            result = await parser.load_events(update=update)
            return result
        finally:
            await parser.close()
    return None
