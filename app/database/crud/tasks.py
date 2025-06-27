from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import TaskScheduler
from app.database.crud.mixines import GetBackNextIdMixin
from database import SessionDep


def get_task_repository(session: SessionDep) -> "TaskRepository":
    return TaskRepository(session)


class TaskRepository(GetBackNextIdMixin[TaskScheduler]):
    model = TaskScheduler

    async def get_tasks(self) -> Sequence[TaskScheduler]:
        stmt = select(self.model).options(
            selectinload(self.model.advertisement),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
