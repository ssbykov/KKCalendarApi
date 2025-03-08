from typing import Any

from starlette.exceptions import HTTPException

from crud.mixines import GetBackNextIdMixin, CommonMixin
from database import SessionDep, Event


def get_event_repository(session: SessionDep) -> "EventRepository":
    return EventRepository(session)


class EventRepository(CommonMixin[Event], GetBackNextIdMixin[Event]):
    model = Event

    async def get_event_by_name(self, name: str) -> Event | None:
        stmt = self.main_stmt.where(Event.name == name)
        event = await self.session.scalar(stmt)
        if event:
            return event
        return None
