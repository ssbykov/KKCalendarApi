from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import ActionNextBackMixin
from crud.days_info import DayInfoRepository
from database import DayInfo


class DayInfoAdmin(
    ModelView,
    ActionNextBackMixin[DayInfo],
    model=DayInfo,
):
    repo_type = DayInfoRepository
    name_plural = "Дни календаря"
    name = "Информация по дню"
    column_labels = {
        "date": "Дата",
        "moon_day": "Лунный день",
        "elements": "Элементы",
        "la": "Энергия Ла",
        "haircutting": "Стрижка",
        "arch": "Световая арка",
        "yelam": "Йелам",
        "events": "События дня",
    }
    column_list = [DayInfo.date, DayInfo.events, DayInfo.moon_day]
    page_size = 25
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
    column_default_sort = (DayInfo.date, True)

    can_create = False
    can_delete = False
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return self.is_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return self.is_superuser(request)
