from crud.mixines import GetBackNextIdMixin
from database import EventType


class EventTypeRepository(GetBackNextIdMixin[EventType]):
    model = EventType
