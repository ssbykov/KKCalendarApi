from markupsafe import Markup
from sqladmin import ModelView

from database import Event, DayInfo


class EventAdmin(ModelView, model=Event):
    name_plural = "События"
    name = "Информация по событию"
    column_list = [
        Event.name,
        Event.en_name,
        Event.ru_name,
    ]
    column_searchable_list = [Event.en_name, Event.ru_name]

    column_formatters_detail = {
        Event.ru_text: lambda model, attribute: Markup(
            formater(getattr(model, "ru_text", ""))
        ),
        Event.en_text: lambda model, attribute: Markup(
            formater(getattr(model, "en_text", ""))
        ),
    }

    column_details_exclude_list = [
        Event.id,
    ]


def formater(column: str) -> str:
    return f'<div style="white-space: pre-wrap; word-wrap: break-word; max-width: 500px;">{column}</div>'


class DayInfoAdmin(ModelView, model=DayInfo):
    name_plural = "Дни календаря"
    name = "Информация по дню"
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
