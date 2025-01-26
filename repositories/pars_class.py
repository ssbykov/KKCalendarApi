from datetime import datetime

import requests
from bs4 import BeautifulSoup as bs
from fake_headers import Headers  # type: ignore

from database.session import SessionDep
from repositories.day_info_repo import DayInfoRepository
from schemas.day_info import ParthDayInfoSchema


class CalendarDayPars:
    HOST = "https://www.karmakagyucalendar.org/current-calendar"
    MONTHS_TAG = "CjVfdc"
    DAY_TAG = "n8H08c UVNKR"

    def __init__(self, session: SessionDep):
        self.headers = Headers(browser='chrome', os='win').generate()
        self.repo = DayInfoRepository(session)
        self._descriptions: list[str] = []

    async def get_days_info(self) -> None:
        # Получаем HTML документ
        response = requests.get(self.HOST)
        doc = bs(response.text, 'html.parser')

        # Извлечение месяцев
        months = []
        for month_element in doc.find_all(class_=self.MONTHS_TAG):
            parsed_list = month_element.get_text().split(" ")
            if len(parsed_list) == 2 and len(parsed_list[-1]) == 4 and parsed_list[-1].isdigit():
                month_year_str = month_element.get_text()
                calendar_date = datetime.strptime(month_year_str, "%B %Y").date()
                months.append(calendar_date)

        # Обработка блоков с днями
        days_info: list[ParthDayInfoSchema] = []
        for index, block in enumerate(doc.find_all(class_=self.DAY_TAG)):
            for day in block.find_all(class_="zfr3Q CDt4Ke"):
                day_list = day.get_text().split(" ⋅ ")

                # Установка дня месяца
                day_number = int(day_list[0].split(" ")[0])
                month = months[index]
                pars_date = month.replace(day=day_number)

                moon_data = day_list[0].split(":")[1].strip(" .")
                moon, moon_day = moon_data.split(".")

                first_element, second_element = await self._find_elements(day_list)
                arch_id = await self.repo.get_arch_id(moon_day)
                la_id = await self.repo.get_la_id(moon_day)
                haircutting_id = await self.repo.get_haircutting_day_id(moon_day)
                yelam_id = await self.repo.get_yelam_day_id(moon)
                day_info = ParthDayInfoSchema(
                    date=str(pars_date),
                    moon_day=moon_data,
                    first_element_id=first_element,
                    second_element_id=second_element,
                    arch_id=arch_id,
                    la_id=la_id,
                    yelam_id=yelam_id,
                    haircutting_id=haircutting_id
                )
                days_info.append(day_info)
        await self.repo.add_days(days_info)
                # links = [(a.get_text().strip(), a['href']) for a in day.find_all('a')]
                #
                # filter_words = ["🌑", "100 times day", "🌕", "10000000 times day", "100000 times day"]
                # description_list = [
                #     (next((link for link in links if link[0] == item.strip()), (item.strip(), "")))
                #     for item in day_list[1:elements_index] if item not in filter_words
                # ]
                #
                # elements_value = day_list[elements_index]
                #
                # tibet_day_info = next(
                #     (item.split(": ") for item in day_list if item.split(":")[0] in self.tibet_days),
                #     (None, None))
                # tibet_day, do_not = tibet_day_info
                #
                # la: str | None = next((item.split(":")[1].strip() for item in day_list if item.startswith("LA")),
                #                       None)
                # yelam: str | None = next(
                #     (item.split(":")[1].strip() for item in day_list if item.startswith("Yelam")), None)
                #
                # haircutting_day_info = next(item for item in day_list if "haircutting day" in item)

    async def _find_elements(self, day_list: list[str], ) -> tuple[int, int]:
        elements = await self.repo.get_elements()
        for i in range(len(elements)):
            for j in range(len(elements)):
                combined_element = f"{elements[i].name}-{elements[j].name}"
                if combined_element in day_list:
                    return elements[i].id, elements[j].id
        raise ValueError
