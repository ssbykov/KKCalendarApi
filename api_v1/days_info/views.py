from datetime import date
from typing import List, Annotated

from fastapi import APIRouter, Depends
from typing_extensions import Sequence

from api_v1.days_info.crud import DayInfoRepository, get_day_info_repository
from database import DayInfo
from database.schemas import DayInfoSchema

router = APIRouter(tags=["Days info"])


@router.get("/all", response_model=List[DayInfoSchema] | str)
async def get_all_days(
    repo: Annotated[DayInfoRepository, Depends(get_day_info_repository)],
) -> Sequence[DayInfo] | str:
    try:
        all_days = await repo.get_all_days()
        return all_days
    except Exception as e:
        return f"Произошла ошибка: {e}"


@router.get("/", response_model=DayInfoSchema | str)
async def get_day_info(
    day: date, repo: Annotated[DayInfoRepository, Depends(get_day_info_repository)]
) -> DayInfo | str:
    return await repo.get_day_by_day(day=day)
