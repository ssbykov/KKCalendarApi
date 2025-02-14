from datetime import date
from typing import Sequence, Any, Dict

from fastapi import HTTPException
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api_v1.mixines import GetBackNextIdMixin
from app.database import (
    DayInfo,
    Elements,
    HaircuttingDay,
    LaPosition,
    Yelam,
    SkylightArch,
    Event,
    Base,
    SessionDep,
)
from app.database.models import DayInfoEvent
from app.database.schemas import DayInfoSchemaCreate, EventSchemaCreate


def get_day_info_repository(session: SessionDep) -> "DayInfoRepository":
    return DayInfoRepository(session)


class DayInfoRepository(GetBackNextIdMixin):
    session: AsyncSession
    model = DayInfo

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.session = session
        self.main_stmt = select(DayInfo).options(
            selectinload(DayInfo.elements),
            selectinload(DayInfo.arch),
            selectinload(DayInfo.la),
            selectinload(DayInfo.yelam),
            selectinload(DayInfo.haircutting),
            selectinload(DayInfo.events),
        )

    @staticmethod
    async def _get_id(session: AsyncSession, model: type[Base], condition: Any) -> int:
        """Общий метод для получения ID объекта по условию."""
        stmt = select(model).where(condition)
        result = await session.scalar(stmt)
        if not result:
            raise ValueError("Параметр не найден!")
        return result.id

    async def get_all_days(self) -> Sequence[DayInfo]:
        result = await self.session.execute(self.main_stmt)
        day_info_list = result.scalars().all()
        return day_info_list

    async def get_day_by_day(self, day: date) -> DayInfo:
        stmt = self.main_stmt.where(DayInfo.date == str(day))
        day_info = await self.session.scalar(stmt)
        if day_info:
            return day_info
        raise HTTPException(status_code=404, detail=f"День с датой {date} не найден")

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

    async def get_event_id(self, event: EventSchemaCreate) -> int | None:
        try:
            return await self._get_id(
                self.session,
                Event,
                Event.name == event.name and Event.link == event.link,
            )
        except ValueError:
            return None

    async def add_event(self, event: EventSchemaCreate) -> int:
        orm_event = event.to_orm()
        self.session.add(orm_event)
        await self.session.flush()
        event_id = orm_event.id
        await self.session.commit()
        return event_id

    async def ru_name_event_update(self, event_id: int, ru_name: str) -> None:
        update_stmt = update(Event).where(Event.id == event_id).values(ru_name=ru_name)
        await self.session.execute(update_stmt)
        await self.session.commit()

    async def add_days(self, days_info: list[DayInfoSchemaCreate]) -> None:
        """
        Добавляет новые записи в таблицу `day_info` и обновляет существующие, если данные отличаются.

        :param days_info: список объектов `DayInfoSchemaCreate` с новыми или обновленными данными.
        """
        # Определяем диапазон дат для выборки из базы
        start_date = min(days_info, key=lambda d: d.date).date
        end_date = max(days_info, key=lambda d: d.date).date

        # Запрос к БД: загружаем существующие записи в указанном диапазоне с descriptions
        stmt = (
            select(DayInfo)
            .options(selectinload(DayInfo.events))
            .filter(DayInfo.date.between(start_date, end_date))
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
