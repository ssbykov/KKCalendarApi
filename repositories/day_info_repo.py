from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.day_info import DayInfo


# @router.get("/haircutting")
# async def get_haircutting_days(session: SessionDep):
#     result = await session.execute(select(HaircuttingModel))
#     return result.scalars().all()

class DayInfoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.main_request = (
            select(DayInfo)
            .options(
                selectinload(DayInfo.first_element),
                selectinload(DayInfo.second_element),
                selectinload(DayInfo.arch),
                selectinload(DayInfo.la),
                selectinload(DayInfo.yelam),
                selectinload(DayInfo.haircutting),
                selectinload(DayInfo.descriptions)
            )
        )

    async def get_all_days(self) -> Sequence[DayInfo]:
        result = await self.session.execute(self.main_request)
        day_info_list = result.scalars().all()
        return day_info_list

    async def get_day_by_date(self, date: str) -> DayInfo:
        request = self.main_request.filter(DayInfo.date == date)
        result = await self.session.execute(request)
        day_info = result.scalars().first()
        return day_info
