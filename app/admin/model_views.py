from markupsafe import Markup
from sqladmin import ModelView

from app.admin.mixines import ActionNextBackMixin
from app.api_v1.days_info.crud import DayInfoRepository
from crud.events import EventRepository
from app.database import Event, DayInfo


class EventAdmin(ActionNextBackMixin, ModelView, model=Event):
    repo_type = EventRepository
    name_plural = "События"
    name = "Информация по событию"
    column_list = [
        Event.name,
        Event.en_name,
        Event.ru_name,
    ]
    column_searchable_list = [Event.en_name, Event.ru_name]
    details_template = "details.html"
    column_formatters_detail = {
        Event.ru_text: lambda model, attribute: Markup(
            formater(getattr(model, "ru_text", ""))
        ),
        Event.en_text: lambda model, attribute: Markup(
            formater(getattr(model, "en_text", ""))
        ),
        Event.link: lambda model, attribute: Markup(
            f'<a href="{getattr(model, "link", "#")}" target="_blank">{getattr(model, "link", "No URL")}</a>'
        ),
    }

    column_details_exclude_list = [
        Event.id,
    ]


def formater(column: str) -> str:
    return f'<div style="white-space: pre-wrap; word-wrap: break-word; max-width: 500px;">{column}</div>'


class DayInfoAdmin(ActionNextBackMixin, ModelView, model=DayInfo):
    repo_type = DayInfoRepository
    name_plural = "Дни календаря"
    name = "Информация по дню"
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
