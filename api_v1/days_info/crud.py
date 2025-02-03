from datetime import date
from typing import Sequence, Optional

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import (
    DayInfo,
    Element,
    HaircuttingDay,
    LaPosition,
    Yelam,
    SkylightArch,
    Description,
)
from database.schemas import DayInfoSchemaCreate


class DayInfoRepository:
    _instance: Optional["DayInfoRepository"] = None

    def __new__(cls, session: AsyncSession) -> "DayInfoRepository":
        if cls._instance is None:
            cls._instance = super(DayInfoRepository, cls).__new__(cls)
            cls._instance.session = session
        return cls._instance

    def __init__(self, session: AsyncSession):
        self.session = session
        self.main_stmt = select(DayInfo).options(
            selectinload(DayInfo.first_element),
            selectinload(DayInfo.second_element),
            selectinload(DayInfo.arch),
            selectinload(DayInfo.la),
            selectinload(DayInfo.yelam),
            selectinload(DayInfo.haircutting),
            selectinload(DayInfo.descriptions),
        )

    async def get_all_days(self) -> Sequence[DayInfo]:
        result = await self.session.execute(self.main_stmt)
        day_info_list = result.scalars().all()
        return day_info_list

    async def get_day_by_day(self, day: date) -> DayInfo:
        request = self.main_stmt.where(DayInfo.date == str(day))
        result = await self.session.execute(request)
        day_info = result.scalars().first()
        if day_info:
            return day_info
        raise HTTPException(status_code=404, detail=f"День с датой {date} не найден")

    async def get_elements(self) -> Sequence[Element]:
        result = await self.session.execute(select(Element))
        elements = result.scalars().all()
        if elements:
            return elements
        raise ValueError("Элементы не найдены")

    async def get_haircutting_day_id(self, moon_day: int) -> int:
        stmt = select(HaircuttingDay).where(HaircuttingDay.moon_day == moon_day)
        result = await self.session.execute(stmt)
        haircutting_day = result.scalars().first()
        if haircutting_day:
            return haircutting_day.id
        raise ValueError("День стрижки не найден")

    async def get_la_id(self, moon_day: int) -> int:
        stmt = select(LaPosition).where(LaPosition.moon_day == moon_day)
        result = await self.session.execute(stmt)
        la_id = result.scalars().first()
        if la_id:
            return la_id.id
        raise ValueError("День Ла не найден")

    async def get_yelam_day_id(self, moon: str) -> int:
        month = moon[:-1] if len(moon) == 3 else moon
        stmt = select(Yelam).where(Yelam.month == int(month))
        result = await self.session.execute(stmt)
        yelam_id = result.scalars().first()
        if yelam_id:
            return yelam_id.id
        raise ValueError("Йелам не найден")

    async def get_arch_id(self, moon_day: str) -> int:
        stmt = select(SkylightArch).where(SkylightArch.moon_day == int(moon_day[-1]))
        result = await self.session.execute(stmt)
        arch_id = result.scalars().first()
        if arch_id:
            return arch_id.id
        raise ValueError("Арка не найдена")

    async def add_days(self, days_info: list[DayInfoSchemaCreate]) -> None:
        """
        Добавляет новые записи в таблицу `day_info` и обновляет существующие, если данные отличаются.

        :param days_info: список объектов `DayInfoSchemaCreate` с новыми или обновленными данными.
        """
        # Определяем диапазон дат для выборки из базы
        start_date = min(days_info, key=lambda day_info: day_info.date).date
        end_date = max(days_info, key=lambda day_info: day_info.date).date

        # Запрос к БД: загружаем существующие записи в указанном диапазоне с descriptions
        query = (
            select(DayInfo)
            .options(selectinload(DayInfo.descriptions))
            .filter(DayInfo.date.between(start_date, end_date))
        )
        result = await self.session.execute(query)

        # Создаем словари для быстрого доступа к существующим данным
        days_dict_in_base = {}  # Данные в виде словаря (date -> dict)
        days_info_in_base = {}  # Объекты DayInfo из базы (date -> объект DayInfo)

        desc_key = "descriptions"
        for day in result.scalars():
            day_to_dict = day.to_dict()
            day_to_dict[desc_key] = [
                desc.to_dict() for desc in day_to_dict.get(desc_key)  # type: ignore
            ]
            days_dict_in_base[day.date] = day_to_dict
            days_info_in_base[day.date] = day

        # Обрабатываем новые и обновленные данные
        for day_info in days_info:
            # Преобразуем объект `DayInfoSchemaCreate` в словарь
            day_dump = day_info.model_dump()
            day_date = day_dump["date"]

            if day_date not in days_info_in_base:
                # Если даты нет в базе — создаем новую запись
                new_day = DayInfoSchemaCreate(**day_dump).to_orm()
                self.session.add(new_day)
            else:
                # Если дата есть, проверяем, изменились ли данные
                db_day = days_info_in_base[day_date]
                if day_dump != days_dict_in_base[day_date]:
                    for key, value in day_dump.items():
                        if key != desc_key:
                            setattr(db_day, key, value)

                    # Обновляем descriptions только если они изменились
                    if day_dump[desc_key] != days_dict_in_base[day_date][desc_key]:
                        await self.session.execute(
                            delete(Description).where(
                                Description.day_info_id == db_day.id
                            )
                        )
                        # Добавляем новые descriptions
                        db_day.descriptions = [
                            Description(**desc) for desc in day_dump[desc_key]
                        ]

        await self.session.commit()
