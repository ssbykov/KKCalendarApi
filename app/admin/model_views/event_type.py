from starlette.requests import Request

from admin.custom_model_view import CustomModelView
from admin.utils import check_superuser
from database.crud.event_type import EventTypeRepository
from database.models import EventType


class EventTypeAdmin(
    CustomModelView[EventType],
    model=EventType,
):
    repo_type = EventTypeRepository
    name_plural = "Типы событий"
    name = "Тип события"
    icon = "fa-solid fa-bars"
    category = "Раздел событий"

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
    can_export = False

    form_ajax_refs = {
        "events": {
            "fields": ("ru_name",),
        }
    }

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
