from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import CustomNavMixin
from admin.utils import check_superuser
from crud.la_positions import LaPositionRepository
from database import LaPosition


class LaPositionAdmin(
    ModelView,
    CustomNavMixin[LaPosition],
    model=LaPosition,
):
    repo_type = LaPositionRepository
    name_plural = "Энергия Ла"
    name = "Энергия Ла"
    category = "Атрибуты дня"

    column_labels = {
        "moon_day": "Лунный день",
        "en_name": "Заголовок на английском",
        "ru_name": "Заголовок на русском",
    }
    column_list = [LaPosition.moon_day, LaPosition.ru_name]
    column_details_list = [
        LaPosition.moon_day,
        LaPosition.en_name,
        LaPosition.ru_name,
    ]
    can_edit = False
    can_delete = False
    can_export = False
    can_create = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
