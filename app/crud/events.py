from sqlalchemy import update, func
from sqlalchemy.orm import selectinload

from crud.mixines import GetBackNextIdMixin
from database import SessionDep, Event, EventSchemaCreate


def get_event_repository(session: SessionDep) -> "EventRepository":
    return EventRepository(session)


class EventRepository(GetBackNextIdMixin[Event]):
    model = Event

    async def get_event_by_name(self, name: str) -> Event | None:
        stmt = self.main_stmt.where(
            func.upper(self.model.name) == func.upper(name)
        ).options(selectinload(Event.days))
        return await self.session.scalar(stmt)

    async def ru_name_event_update(self, event_id: int, ru_name: str) -> None:
        update_stmt = (
            update(self.model).where(self.model.id == event_id).values(ru_name=ru_name)
        )
        await self.session.execute(update_stmt)
        await self.session.commit()

    async def add_event(self, event: EventSchemaCreate) -> int:
        orm_event = event.to_orm()
        self.session.add(orm_event)
        await self.session.flush()
        event_id = orm_event.id
        await self.session.commit()
        return event_id
