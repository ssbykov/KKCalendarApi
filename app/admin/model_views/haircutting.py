from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.database.crud.haircutting_days import HaircuttingRepository
from app.database import HaircuttingDay


class HaircuttingAdmin(
    CustomModelView[HaircuttingDay],
    model=HaircuttingDay,
):
    repo_type = HaircuttingRepository
    name_plural = "Дни для стрижки"
    name = "День для стрижки"
    category = "Атрибуты дня"

    column_labels = {
        "moon_day": "Лунный день",
        "en_name": "Заголовок на английском",
        "ru_name": "Заголовок на русском",
        "is_inauspicious": "Благоприятность",
    }
    column_list = ("moon_day", "ru_name")
    column_details_list = (
        "moon_day",
        "en_name",
        "ru_name",
        "is_inauspicious",
    )
    can_edit = False
    can_delete = False
    can_export = False
    can_create = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
