from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.database.crud.emoji import EmojiRepository
from app.database.models import Emoji


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
