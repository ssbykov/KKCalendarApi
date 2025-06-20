from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser, text_formater
from app.database.crud.elements import ElementsRepository
from app.database import Elements


class ElementsAdmin(
    CustomModelView[Elements],
    model=Elements,
):
    repo_type = ElementsRepository
    name_plural = "Сочетания элементов"
    name = "Сочетание элементов"
    category = "Атрибуты дня"

    column_list = ("ru_name", "is_positive")
    column_labels = {
        "en_name": "Заголовок на английском",
        "ru_name": "Заголовок на русском",
        "ru_text": "Описание на русском",
        "en_text": "Описание на русском",
        "is_positive": "Позитивный",
    }
    column_details_list = (
        "en_name",
        "ru_name",
        "en_text",
        "ru_text",
        "is_positive",
    )
    can_edit = False
    can_delete = False
    can_export = False
    can_create = False

    column_formatters_detail = text_formater(Elements)

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
