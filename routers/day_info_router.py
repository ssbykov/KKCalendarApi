from typing import List

from typing_extensions import Sequence

from models.day_info import DayInfo
from repositories.day_info_repo import DayInfoRepository
from database.session import SessionDep
from fastapi import APIRouter

from schemas.day_info import DayInfoSchema

router = APIRouter()


@router.get("/days", response_model=List[DayInfoSchema])
async def get_all_days(session: SessionDep) -> Sequence[DayInfo]:
    repo = DayInfoRepository(session)
    all_days = await repo.get_all_days()
    return all_days


@router.get("/days/{date}", response_model=DayInfoSchema)
async def get_day_info(date: str, session: SessionDep) -> DayInfo:
    repo = DayInfoRepository(session)
    return await repo.get_day_by_date(date=date)
