from typing import Annotated, Sequence, List

from fastapi import APIRouter, Depends

from api.api_v1.fastapi_users import current_super_user
from app.core import settings
from app.database.crud.tasks import TaskRepository, get_task_repository
from database import TaskScheduler
from database.models import User
from database.schemas.task import TaskSchema

router = APIRouter(
    tags=["Tasks"],
    prefix=settings.api.v1.tasks,
)
router.include_router(
    router,
)


@router.get("/", response_model=List[TaskSchema])
async def get_all(
    repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user: Annotated[User, Depends(current_super_user)],
) -> Sequence[TaskScheduler] | str:
    try:
        return await repo.get_tasks()
    except Exception as e:
        return f"Произошла ошибка: {e}"
