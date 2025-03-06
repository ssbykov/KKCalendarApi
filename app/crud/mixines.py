from abc import ABC, abstractmethod
from typing import (
    Callable,
    Any,
    Optional,
    Type,
    Sequence,
    Generic,
)

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from core.type_vars import T


class GetBackNextIdMixin(ABC, Generic[T]):
    session: AsyncSession

    @property
    @abstractmethod
    def model(self) -> Type[T]:
        pass

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_adjacent_id(
        self,
        current_id: int,
        condition: Callable[[InstrumentedAttribute[int], Any], Any],
        order: Any,
        list_query: Select[Any],
    ) -> Optional[int]:
        """
        Вспомогательный метод для получения следующего или предыдущего ID события.

        Args:
            current_id: Текущий ID события.
            condition: Функция, определяющая условие WHERE (например, Event.id > current_id).
            order:  Выражение order_by (например, Event.id.asc() или Event.id.desc()).

        Returns:
            Следующий или предыдущий ID события, или None, если такого ID нет.
        """
        stmt = (
            list_query.where(condition(self.model.id, current_id))
            .order_by(order)
            .limit(1)
        )
        result = await self.session.scalar(stmt)
        return result.id if result else None

    async def get_next_id(
        self, current_id: int, list_query: Select[Any]
    ) -> Optional[int]:
        """
        Получает следующий ID события после указанного.
        """
        return await self._get_adjacent_id(
            current_id=current_id,
            condition=lambda id_attr, cid: id_attr > cid,
            order=self.model.id.asc(),
            list_query=list_query,
        )

    async def get_back_id(
        self, current_id: int, list_query: Select[Any]
    ) -> Optional[int]:
        """
        Получает предыдущий ID события перед указанным.
        """
        return await self._get_adjacent_id(
            current_id=current_id,
            condition=lambda id_attr, cid: id_attr < cid,
            order=self.model.id.desc(),
            list_query=list_query,
        )


class CommonMixin(ABC, Generic[T]):
    session: AsyncSession

    @property
    @abstractmethod
    def model(self) -> Type[T]:
        pass

    def __init__(self, session: AsyncSession):
        self.session = session
        self.main_stmt = select(self.model)

    async def get_all(self) -> Sequence[T]:
        result = await self.session.execute(self.main_stmt)
        obj_list = result.scalars().all()
        return obj_list
