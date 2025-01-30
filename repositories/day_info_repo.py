from typing import Sequence, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models import *
from schemas.day_info import ParthDayInfoSchema


class DayInfoRepository:
    _instance: Optional["DayInfoRepository"] = None

    def __new__(cls, session: AsyncSession) -> "DayInfoRepository":
        if cls._instance is None:
            cls._instance = super(DayInfoRepository, cls).__new__(cls)
            cls._instance.session = session
        return cls._instance

    def __init__(self, session: AsyncSession):
        self.session = session
        self.main_request = select(DayInfo).options(
            selectinload(DayInfo.first_element),
            selectinload(DayInfo.second_element),
            selectinload(DayInfo.arch),
            selectinload(DayInfo.la),
            selectinload(DayInfo.yelam),
            selectinload(DayInfo.haircutting),
            selectinload(DayInfo.descriptions),
        )

    async def get_all_days(self) -> Sequence[DayInfo]:
        result = await self.session.execute(self.main_request)
        day_info_list = result.scalars().all()
        return day_info_list

    async def get_day_by_date(self, date: str) -> DayInfo:
        request = self.main_request.filter(DayInfo.date == date)
        result = await self.session.execute(request)
        day_info = result.scalars().first()
        if day_info:
            return day_info
        raise ValueError(f"День с датой {date} не найден")

    async def get_elements(self) -> Sequence[ElementModel]:
        result = await self.session.execute(select(ElementModel))
        elements = result.scalars().all()
        if elements:
            return elements
        raise ValueError("Элементы не найдены")

    async def get_haircutting_day_id(self, moon_day: int) -> int:
        request = select(HaircuttingModel).filter(HaircuttingModel.moon_day == moon_day)
        result = await self.session.execute(request)
        haircutting_day = result.scalars().first()
        if haircutting_day:
            return haircutting_day.id
        raise ValueError("День стрижки не найден")

    async def get_la_id(self, moon_day: int) -> int:
        request = select(LaModel).filter(LaModel.moon_day == moon_day)
        result = await self.session.execute(request)
        la_id = result.scalars().first()
        if la_id:
            return la_id.id
        raise ValueError("День Ла не найден")

    async def get_yelam_day_id(self, moon: str) -> int:
        month = moon[:-1] if len(moon) == 3 else moon
        request = select(YelamModel).filter(YelamModel.month == int(month))
        result = await self.session.execute(request)
        yelam_id = result.scalars().first()
        if yelam_id:
            return yelam_id.id
        raise ValueError("Йелам не найден")

    async def get_arch_id(self, moon_day: str) -> int:
        request = select(ArchModel).filter(ArchModel.moon_day == int(moon_day[-1]))
        result = await self.session.execute(request)
        arch_id = result.scalars().first()
        if arch_id:
            return arch_id.id
        raise ValueError("Арка не найдена")

    async def add_days(self, days_info: list[ParthDayInfoSchema]) -> None:
        days = (day_info.to_orm() for day_info in days_info)
        self.session.add_all(days)
        await self.session.flush()
        await self.session.commit()
