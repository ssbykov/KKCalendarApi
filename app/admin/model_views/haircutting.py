from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import ActionNextBackMixin, CommonActionsMixin
from crud.haircutting import HaircuttingRepository
from database import HaircuttingDay


class HaircuttingAdmin(
    ModelView,
    ActionNextBackMixin[HaircuttingDay],
    CommonActionsMixin[HaircuttingDay],
    model=HaircuttingDay,
):
    repo_type = HaircuttingRepository
    name_plural = "Дни для стрижки"
    name = "День для стрижки"
    column_labels = {
        "moon_day": "Лунный день",
        "en_name": "Заголовок на английском",
        "ru_name": "Заголовок на русском",
        "is_inauspicious": "Благоприятность",
    }
    column_details_list = [
        HaircuttingDay.moon_day,
        HaircuttingDay.en_name,
        HaircuttingDay.ru_name,
        HaircuttingDay.is_inauspicious,
    ]
    can_edit = False
    can_delete = False

    def is_visible(self, request: Request) -> bool:
        return self.is_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return self.is_superuser(request)
