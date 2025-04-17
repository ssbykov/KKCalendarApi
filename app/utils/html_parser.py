from datetime import datetime

import requests
from bs4 import BeautifulSoup as bs
from fake_headers import Headers  # type: ignore

from core import settings
from crud.days_info import DayInfoRepository
from crud.events import EventRepository
from crud.users import UsersRepository
from database import SessionDep
from database.schemas import DayInfoSchemaCreate, EventSchemaCreate
from utils.translator import translate


class HtmlParser:
    HOST = "https://www.karmakagyucalendar.org/current-calendar"
    MONTHS_TAG = "CjVfdc"
    DAY_TAG = "n8H08c UVNKR"

    def __init__(self, session: SessionDep):
        self.headers = Headers(browser="chrome", os="win").generate()
        self.session = session
        self.day_info_repo = DayInfoRepository(self.session)
        self.event_repo = EventRepository(self.session)

    async def get_days_info(self) -> None:
        # Получаем HTML документ
        response = requests.get(self.HOST)
        doc = bs(response.text, "html.parser")

        # Извлечение месяцев
        months = []
        for month_element in doc.find_all(class_=self.MONTHS_TAG):
            parsed_list = month_element.get_text().split(" ")
            if (
                len(parsed_list) == 2
                and len(parsed_list[-1]) == 4
                and parsed_list[-1].isdigit()
            ):
                month_year_str = month_element.get_text()
                calendar_date = datetime.strptime(month_year_str, "%B %Y").date()
                months.append(calendar_date)

        # Обработка блоков с днями
        days_info: list[DayInfoSchemaCreate] = []
        events_for_translate = {}
        for index, block in enumerate(doc.find_all(class_=self.DAY_TAG)):
            user_repo = UsersRepository(self.session)
            user_id = await user_repo.get_user_id(settings.super_user.email)
            for day in block.find_all(class_="zfr3Q CDt4Ke"):
                day_list = day.get_text().split(" ⋅ ")

                # Установка дня месяца
                day_number = int(day_list[0].split(" ")[0])
                month = months[index]
                pars_date = month.replace(day=day_number)

                moon_data = day_list[0].split(":")[1].strip(" .")
                moon, moon_day = moon_data.split(".")

                elements_id, elements_index = await self._find_elements(day_list)
                arch_id = await self.day_info_repo.get_arch_id(moon_day)
                la_id = await self.day_info_repo.get_la_id(int(moon_day))
                haircutting_id = await self.day_info_repo.get_haircutting_day_id(
                    int(moon_day)
                )
                yelam_id = await self.day_info_repo.get_yelam_day_id(moon)
                links = [(a.get_text().strip(), a["href"]) for a in day.find_all("a")]
                filter_words = (
                    "🌑",
                    "🌕",
                    "10 000 000 times day",
                    "1 000 000 times day",
                    "100 000 times day",
                    "10 000 times day",
                    "1 000 times day",
                    "100 times day",
                )
                parsed_events = [
                    (
                        next(
                            (link for link in links if link[0] == item.strip()),
                            (item.strip(), ""),
                        )
                    )
                    for item in day_list[1:elements_index]
                    if item not in filter_words
                ]
                events_schema = list(
                    EventSchemaCreate(
                        name=event[0],
                        en_name=event[0],
                        ru_name=event[0],
                        link=event[1],
                        user_id=int(user_id) if user_id else None,
                    )
                    for event in parsed_events
                )
                events = []
                for event in events_schema:
                    event_in_base = await self.event_repo.get_event_by_name(event.name)
                    if event_in_base:
                        events.append(event_in_base.id)
                    else:
                        new_event_id = await self.event_repo.add_event(event)
                        events_for_translate[new_event_id] = event.en_name
                        events.append(new_event_id)

                day_info = DayInfoSchemaCreate(
                    date=str(pars_date),
                    moon_day=moon_data,
                    elements_id=elements_id,
                    arch_id=arch_id,
                    la_id=la_id,
                    yelam_id=yelam_id,
                    haircutting_id=haircutting_id,
                    events=events,
                )
                days_info.append(day_info)
        translated_events = translate("|".join(events_for_translate.values())).split(
            "|"
        )
        for event_id, ru_name in zip(events_for_translate.keys(), translated_events):
            await self.event_repo.ru_name_event_update(event_id, ru_name)

        await self.day_info_repo.add_days(days_info)

    async def _find_elements(
        self,
        day_list: list[str],
    ) -> tuple[int, int]:
        elements = await self.day_info_repo.get_elements()
        result = [
            (el.id, day_list.index(el.en_name))
            for el in elements
            if el.en_name in day_list
        ]
        if result:
            return result[0]
        raise ValueError
