from typing import Sequence, Any, Dict

from fastapi import HTTPException
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.mixines import GetBackNextIdMixin, CommonMixin
from database import (
    DayInfo,
    Elements,
    HaircuttingDay,
    LaPosition,
    Yelam,
    SkylightArch,
    BaseWithId,
    SessionDep,
)
from database import DayInfoEvent, DayInfoSchemaCreate


def get_day_info_repository(session: SessionDep) -> "DayInfoRepository":
    return DayInfoRepository(session)


class DayInfoRepository(GetBackNextIdMixin[DayInfo], CommonMixin[DayInfo]):
    session: AsyncSession
    model = DayInfo

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.session = session
        self.main_stmt = select(self.model).options(
            selectinload(self.model.elements),
            selectinload(self.model.arch),
            selectinload(self.model.la),
            selectinload(self.model.yelam),
            selectinload(self.model.haircutting),
            selectinload(self.model.events),
        )

    @staticmethod
    async def _get_id(
        session: AsyncSession, model: type[BaseWithId], condition: Any
    ) -> int:
        """Общий метод для получения ID объекта по условию."""
        stmt = select(model).where(condition)
        result = await session.scalar(stmt)
        if not result:
            raise ValueError("Параметр не найден!")
        return result.id

    async def get_day_by_date(self, day: str) -> DayInfo:
        return await self._get_day_by(self.model.date == day)

    async def get_day_by_id(self, day_id: str) -> DayInfo:
        return await self._get_day_by(self.model.id == int(day_id))

    async def get_days(self, start_date: str, end_date: str) -> Sequence[DayInfo]:
        stmt = self.main_stmt.where(self.model.date.between(start_date, end_date))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def _get_day_by(self, condition: Any) -> DayInfo:
        stmt = self.main_stmt.where(condition)
        day_info = await self.session.scalar(stmt)
        if day_info:
            return day_info
        raise HTTPException(status_code=404, detail=f"День не найден")

    async def get_elements(self) -> Sequence[Elements]:
        result = await self.session.execute(select(Elements))
        elements = result.scalars().all()
        if elements:
            return elements
        raise ValueError("Элементы не найдены")

    async def get_haircutting_day_id(self, moon_day: int) -> int:
        return await self._get_id(
            self.session, HaircuttingDay, HaircuttingDay.moon_day == moon_day
        )

    async def get_la_id(self, moon_day: int) -> int:
        return await self._get_id(
            self.session, LaPosition, LaPosition.moon_day == moon_day
        )

    async def get_yelam_day_id(self, moon: str) -> int:
        month = moon[:-1] if len(moon) == 3 else moon
        return await self._get_id(self.session, Yelam, Yelam.month == int(month))

    async def get_arch_id(self, moon_day: str) -> int:
        day = int(moon_day[-1])
        return await self._get_id(
            self.session, SkylightArch, SkylightArch.moon_day == day
        )

    async def add_days(self, days_info: list[DayInfoSchemaCreate]) -> None:
        """
        Добавляет новые записи в таблицу `day_info` и обновляет существующие, если данные отличаются.

        """
        # Определяем диапазон дат для выборки из базы
        start_date = min(days_info, key=lambda d: d.date).date
        end_date = max(days_info, key=lambda d: d.date).date

        # Запрос к БД: загружаем существующие записи в указанном диапазоне с descriptions
        stmt = (
            select(self.model)
            .options(selectinload(self.model.events))
            .filter(self.model.date.between(start_date, end_date))
        )
        result = await self.session.execute(stmt)

        # Создаем словари для быстрого доступа к существующим данным
        days_dict_in_base: Dict[str, Any] = {}
        days_info_in_base: Dict[str, DayInfo] = {}

        event_key = "events"
        for day in result.scalars():
            day_to_dict = day.to_dict()
            day_to_dict[event_key] = [
                event.id for event in day_to_dict.get(event_key, [])
            ]
            days_dict_in_base[day.date] = day_to_dict
            days_info_in_base[day.date] = day

        # Обрабатываем новые и обновленные данные
        for day_info in days_info:
            # Преобразуем объект `DayInfoSchemaCreate` в словарь
            day_dump = day_info.model_dump()
            day_date = day_dump["date"]
            event_ids_new = set(day_dump[event_key])

            if day_date not in days_info_in_base:
                # Если даты нет в базе — создаем новую запись
                new_day = DayInfoSchemaCreate(**day_dump).to_orm()
                self.session.add(new_day)
                await self.session.flush()
                for event_id in event_ids_new:
                    await self.session.execute(
                        insert(DayInfoEvent).values(
                            day_info_id=new_day.id, event_id=event_id
                        )
                    )

            else:
                # Если дата есть, проверяем, изменились ли данные
                db_day = days_info_in_base[day_date]
                event_ids_in_base = set(days_dict_in_base[day_date][event_key])
                if day_dump != days_dict_in_base[day_date]:
                    for key, value in day_dump.items():
                        if key != event_key:
                            setattr(db_day, key, value)

                    # Обновляем events только если они изменились
                    events_to_add = event_ids_new - event_ids_in_base
                    events_to_remove = event_ids_in_base - event_ids_new

                    for event_id in events_to_add:
                        await self.session.execute(
                            insert(DayInfoEvent).values(
                                day_info_id=db_day.id, event_id=event_id
                            )
                        )

                    for event_id in events_to_remove:
                        await self.session.execute(
                            delete(DayInfoEvent).where(
                                DayInfoEvent.day_info_id == db_day.id,
                                DayInfoEvent.event_id == event_id,
                            )
                        )

        await self.session.commit()
