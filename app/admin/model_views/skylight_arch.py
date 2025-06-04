from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.database.crud.skylight_arches import SkylightArchRepository
from app.database import SkylightArch


class SkylightArchAdmin(
    CustomModelView[SkylightArch],
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
    column_list = ("moon_day", "name")
    column_details_list = (
        "moon_day",
        "name",
        "en_desc",
        "ru_desc",
    )
    can_edit = False
    can_delete = False
    can_export = False
    can_create = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
