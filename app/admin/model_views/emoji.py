from starlette.requests import Request

from admin.custom_model_view import CustomModelView
from admin.utils import check_superuser
from database.crud.emoji import EmojiRepository
from database.models import Emoji


class EmojiAdmin(
    CustomModelView[Emoji],
    model=Emoji,
):
    repo_type = EmojiRepository
    name_plural = "Эмодзи"
    name = "Эмодзи"
    icon = "fa-solid fa-icons"
    category = "Раздел событий"

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
