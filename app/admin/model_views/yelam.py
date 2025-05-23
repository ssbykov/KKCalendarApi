from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import CustomNavMixin
from admin.utils import check_superuser
from crud.yelams import YelamRepository
from database import Yelam


class YelamAdmin(
    ModelView,
    CustomNavMixin[Yelam],
    model=Yelam,
):
    repo_type = YelamRepository
    name_plural = "Йелам"
    name = "Йелам"
    category = "Атрибуты дня"

    column_labels = {
        "month": "Месяц",
        "en_name": "Название на английском",
        "ru_name": "Название на русском",
    }
    column_list = ["month", "ru_name"]
    column_details_list = [
        Yelam.month,
        Yelam.ru_name,
        Yelam.en_name,
    ]
    can_edit = False
    can_delete = False
    can_export = False
    can_create = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
