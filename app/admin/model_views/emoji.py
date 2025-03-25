from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import CustomNavMixin
from admin.utils import check_superuser
from crud.emoji import EmojiRepository
from database.models import Emoji


class EmojiAdmin(
    ModelView,
    CustomNavMixin[Emoji],
    model=Emoji,
):
    repo_type = EmojiRepository
    name_plural = "Эмодзи"
    name = "Эмодзи"
    column_list = ["name", "emoji"]
    column_details_exclude_list = [
        Emoji.id,
    ]
    column_labels = {
        "name": "Название",
        "emoji": "Эмодзи",
    }
    can_edit = True
    can_delete = True
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
