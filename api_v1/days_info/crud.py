from datetime import date
from typing import Sequence, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database import (
    DayInfo,
    Element,
    HaircuttingDay,
    LaPosition,
    Yelam,
    SkylightArch,
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
        days = (day_info.to_orm() for day_info in days_info)
        self.session.add_all(days)
        await self.session.commit()
