from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import ActionNextBackMixin, CommonActionsMixin
from crud.days_info import DayInfoRepository
from database import DayInfo


class DayInfoAdmin(
    ModelView,
    ActionNextBackMixin,
    CommonActionsMixin,
    model=DayInfo,
):
    repo_type = DayInfoRepository
    name_plural = "Дни календаря"
    name = "Информация по дню"
    column_labels = {
        "date": "Дата",
        "moon_day": "Лунные дни",
        "elements": "Элементы",
        "la": "Энергия Ла",
        "haircutting": "Стрижка",
        "arch": "Световая арка",
        "yelam": "Йелам",
        "events": "События дня",
    }
    details_template = "details.html"
    column_list = [DayInfo.id, DayInfo.date, DayInfo.moon_day]
    column_searchable_list = [DayInfo.date, DayInfo.moon_day]
    column_details_list = [
        DayInfo.date,
        DayInfo.moon_day,
        DayInfo.elements,
        DayInfo.la,
        DayInfo.haircutting,
        DayInfo.arch,
        DayInfo.yelam,
        DayInfo.events,
    ]
    can_create = False
    can_delete = False
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return self.is_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return self.is_superuser(request)

    @staticmethod
    def is_superuser(request: Request) -> bool:
        user = request.session.get("user")
        return isinstance(user, dict) and bool(user.get("is_superuser"))
