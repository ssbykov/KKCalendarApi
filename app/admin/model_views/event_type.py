from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import ActionNextBackMixin
from crud.event_type import EventTypeRepository
from database.models import EventType


class EventTypeAdmin(
    ModelView,
    ActionNextBackMixin[EventType],
    model=EventType,
):
    repo_type = EventTypeRepository
    name_plural = "Типы событий"
    name = "Тип события"
    column_list = ["ru_name", "rank"]
    column_labels = {
        "ru_name": "Название",
        "ru_desc": "Описание",
        "rank": "Ранг",
    }
    can_edit = True
    can_delete = True

    def is_visible(self, request: Request) -> bool:
        return self.is_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return self.is_superuser(request)
