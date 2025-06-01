from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.database.crud.yelams import YelamRepository
from app.database import Yelam


class YelamAdmin(
    CustomModelView[Yelam],
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
