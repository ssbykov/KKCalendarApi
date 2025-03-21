from abc import ABC, abstractmethod
from typing import (
    Any,
    Optional,
    Type,
    Sequence,
    Generic,
)

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.type_vars import T


class GetBackNextIdMixin(ABC, Generic[T]):
    session: AsyncSession

    @property
    @abstractmethod
    def model(self) -> Type[T]:
        pass

    def __init__(self, session: AsyncSession):
        self.session = session
        self.main_stmt = select(self.model)

    async def get_next_id(
        self, current_val: int | str, list_query: Select[Any], sort_column: str = "id"
    ) -> Optional[int]:

        column = getattr(self.model, sort_column)
        stmt = list_query.where(column > current_val).order_by(column.asc()).limit(1)
        result = await self.session.scalar(stmt)
        return result.id if result else None

    async def get_back_id(
        self, current_val: int | str, list_query: Select[Any], sort_column: str = "id"
    ) -> Optional[int]:
        column = getattr(self.model, sort_column)
        stmt = list_query.where(column < current_val).order_by(column.desc()).limit(1)
        result = await self.session.scalar(stmt)
        return result.id if result else None

    async def get_all(self) -> Sequence[T]:
        result = await self.session.execute(self.main_stmt)
        obj_list = result.scalars().all()
        return obj_list

    async def get_by_id(self, obj_id: int) -> T | None:
        result = await self.session.execute(
            self.main_stmt.where(self.model.id == obj_id)
        )
        obj_list = result.scalar()
        return obj_list
