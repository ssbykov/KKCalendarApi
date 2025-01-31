from typing import List

from fastapi import APIRouter
from typing_extensions import Sequence

from database.db_helper import SessionDep
from models import DayInfo
from repositories.day_info_repo import DayInfoRepository
from schemas.day_info import DayInfoSchema
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
async def get_day_info(date: str, session: SessionDep) -> DayInfo | str:
    try:
        date_model = DateSchema(date=date)
        repo = DayInfoRepository(session)
        return await repo.get_day_by_date(date=date_model.date)
    except ValueError as e:
        return f"Ошибка валидации даты: {e}"
    except Exception as e:
        return f"Произошла ошибка: {e}"
