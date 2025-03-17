from crud.mixines import CommonMixin, GetBackNextIdMixin
from database.models import EventPhoto


class EventPhotoRepository(CommonMixin[EventPhoto], GetBackNextIdMixin[EventPhoto]):
    model = EventPhoto
