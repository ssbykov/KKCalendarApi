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
    column_list = ["name", "rank"]
    column_details_exclude_list = [
        EventType.id,
    ]
    column_labels = {
        "name": "Название",
        "desc": "Описание",
        "rank": "Ранг",
        "events": "Cобытия",
    }
    can_edit = True
    can_delete = True

    def is_visible(self, request: Request) -> bool:
        return self.is_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return self.is_superuser(request)
