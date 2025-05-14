from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import CustomNavMixin
from admin.utils import check_superuser
from crud.quote import QuoteRepository
from database import Quote


class QuoteAdmin(
    ModelView,
    CustomNavMixin[Quote],
    model=Quote,
):
    repo_type = QuoteRepository
    name_plural = "Цитаты"
    name = "Цитата"
    icon = "fa-solid fa-quote-left"

    column_list = ["lama", "text"]
    column_details_exclude_list = ("id", "lama_id")
    column_labels = {
        "text": "Цитата",
        "lama": "Автор",
    }
    can_edit = True
    can_delete = True
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
