from typing import List, Annotated

from fastapi import APIRouter, Depends
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse
from typing_extensions import Sequence

from database.crud.days_info import DayInfoRepository, get_day_info_repository
from database.crud.event_photos import EventPhotoRepository, get_event_photos_repository
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


@router.get("/photos/{photo_id}", response_model=None)
async def get_photo(
    photo_id: int,
    repo: Annotated[EventPhotoRepository, Depends(get_event_photos_repository)],
) -> FileResponse | HTTPException:
    return await repo.get_photo_by_id(photo_id=photo_id)
