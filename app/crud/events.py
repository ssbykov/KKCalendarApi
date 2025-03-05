from crud.mixines import GetBackNextIdMixin, CommonMixin
from database import SessionDep, Event


def get_event_repository(session: SessionDep) -> "EventRepository":
    return EventRepository(session)


class EventRepository(CommonMixin, GetBackNextIdMixin):
    model = Event
