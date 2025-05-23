from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import CustomNavMixin
from admin.utils import check_superuser
from crud.skylight_arches import SkylightArchRepository
from database import SkylightArch


class SkylightArchAdmin(
    ModelView,
    CustomNavMixin[SkylightArch],
    model=SkylightArch,
):
    repo_type = SkylightArchRepository
    name_plural = "Световые арки"
    name = "Световая арка"
    category = "Атрибуты дня"

    column_labels = {
        "moon_day": "Лунный день",
        "name": "Название",
        "en_desc": "Описание на английском",
        "ru_desc": "Описание на русском",
    }
    column_list = ["moon_day", "name"]
    column_details_list = [
        SkylightArch.moon_day,
        SkylightArch.name,
        SkylightArch.en_desc,
        SkylightArch.ru_desc,
    ]
    can_edit = False
    can_delete = False
    can_export = False
    can_create = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
