from typing import List, Annotated

from fastapi import APIRouter, Depends
from typing_extensions import Sequence

from crud.days_info import DayInfoRepository, get_day_info_repository
from database import DayInfo, DayInfoSchema

router = APIRouter()


@router.get("/all", response_model=List[DayInfoSchema] | str)
async def get_all_days(
    repo: Annotated[DayInfoRepository, Depends(get_day_info_repository)],
) -> Sequence[DayInfo] | str:
    try:
        all_days = await repo.get_all()
        return all_days
    except Exception as e:
        return f"Произошла ошибка: {e}"


@router.get("/", response_model=List[DayInfoSchema] | str)
async def get_days(
    start_date: str,
    end_date: str,
    repo: Annotated[DayInfoRepository, Depends(get_day_info_repository)],
) -> Sequence[DayInfo] | str:
    return await repo.get_days(start_date=start_date, end_date=end_date)
