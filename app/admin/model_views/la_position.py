from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.database.crud.la_positions import LaPositionRepository
from app.database import LaPosition


class LaPositionAdmin(
    CustomModelView[LaPosition],
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
    column_list = ("moon_day", "ru_name")
    column_details_list = (
        "moon_day",
        "en_name",
        "ru_name",
    )
    can_edit = False
    can_delete = False
    can_export = False
    can_create = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
