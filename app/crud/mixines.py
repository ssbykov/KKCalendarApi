from abc import ABC, abstractmethod
from typing import Callable, Any, Optional, Type, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from database import BaseWithId


class GetBackNextIdMixin(ABC):
    session: AsyncSession

    @property
    @abstractmethod
    def model(self) -> Type[BaseWithId]:
        pass

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_adjacent_id(
        self,
        current_id: int,
        condition: Callable[[InstrumentedAttribute[int], Any], Any],
        order: Any,
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
            select(self.model.id)
            .where(condition(self.model.id, current_id))
            .order_by(order)
            .limit(1)
        )
        result = await self.session.scalar(stmt)
        return result

    async def get_next_id(self, current_id: int) -> Optional[int]:
        """
        Получает следующий ID события после указанного.
        """
        return await self._get_adjacent_id(
            current_id, lambda id_attr, cid: id_attr > cid, self.model.id.asc()
        )

    async def get_back_id(self, current_id: int) -> Optional[int]:
        """
        Получает предыдущий ID события перед указанным.
        """
        return await self._get_adjacent_id(
            current_id, lambda id_attr, cid: id_attr < cid, self.model.id.desc()
        )


T = TypeVar("T", bound="BaseWithId")


class CommonMixin(ABC):
    session: AsyncSession
    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.main_stmt = select(self.model)

    async def get_all(self) -> Sequence[T]:
        result = await self.session.execute(self.main_stmt)
        obj_list = result.scalars().all()
        return obj_list
