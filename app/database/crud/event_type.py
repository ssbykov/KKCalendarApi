from app.database.crud.mixines import GetBackNextIdMixin
from app.database import EventType


class EventTypeRepository(GetBackNextIdMixin[EventType]):
    model = EventType
