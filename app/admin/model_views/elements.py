from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import ActionNextBackMixin, CommonActionsMixin
from crud.elements import ElementsRepository
from database import Elements


class ElementsAdmin(
    ModelView,
    ActionNextBackMixin[Elements],
    CommonActionsMixin[Elements],
    model=Elements,
):
    repo_type = ElementsRepository
    name_plural = "Сочетания элементов"
    name = "Сочетание элементов"
    column_labels = {
        "en_name": "Заголовок на английском",
        "ru_name": "Заголовок на русском",
        "ru_text": "Описание на русском",
        "en_text": "Описание на русском",
        "is_positive": "Позитивный",
    }
    column_details_list = [
        Elements.en_name,
        Elements.ru_name,
        Elements.en_text,
        Elements.ru_text,
        Elements.is_positive,
    ]
    can_edit = False
    can_delete = False

    def is_visible(self, request: Request) -> bool:
        return self.is_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return self.is_superuser(request)
