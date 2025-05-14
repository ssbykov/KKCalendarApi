from sqladmin import ModelView
from sqlalchemy import select
from starlette.requests import Request

from admin.mixines import CustomNavMixin
from admin.utils import check_superuser
from crud.lama import LamaRepository
from database.models import Lama


class LamaAdmin(
    ModelView,
    CustomNavMixin[Lama],
    model=Lama,
):
    repo_type = LamaRepository
    name_plural = "Учителя"
    name = "Лама"
    icon = "fa-solid fa-icons"

    column_list = ["name"]
    column_details_exclude_list = (
        "id",
        "photo_id",
        "lama",
    )
    form_excluded_columns = ("lama",)
    column_labels = {
        "name": "Имя",
        "description": "Описание",
        "photo": "Фотография",
    }
    can_edit = True
    can_delete = True
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
