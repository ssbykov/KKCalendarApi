from typing import List

from fastapi import APIRouter, HTTPException
from typing_extensions import Sequence

from database import SessionDep, DayInfo
from database.schemas import DayInfoSchema
from api_v1.days_info.crud import DayInfoRepository
from datetime import date
from schemas.types import DateSchema

router = APIRouter(prefix="/days", tags=["Days info"])


@router.get("/all", response_model=List[DayInfoSchema] | str)
async def get_all_days(session: SessionDep) -> Sequence[DayInfo] | str:
    try:
        repo = DayInfoRepository(session)
        all_days = await repo.get_all_days()
        return all_days
    except Exception as e:
        return f"Произошла ошибка: {e}"


@router.get("/", response_model=DayInfoSchema | str)
async def get_day_info(day: date, session: SessionDep) -> DayInfo | str:
    repo = DayInfoRepository(session)
    return await repo.get_day_by_day(day=day)
