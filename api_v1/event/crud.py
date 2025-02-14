from api_v1.mixines import GetBackNextIdMixin
from database import SessionDep, Event


def get_event_repository(session: SessionDep) -> "EventRepository":
    return EventRepository(session)


class EventRepository(GetBackNextIdMixin):
    model = Event
