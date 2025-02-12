from sqladmin import ModelView

from database import Event, DayInfo


class EventAdmin(ModelView, model=Event):
    name_plural = "События"
    column_list = [
        Event.name,
        Event.en_name,
        Event.ru_name,
    ]
    column_searchable_list = [Event.en_name, Event.ru_name]


class DayInfoAdmin(ModelView, model=DayInfo):
    name_plural = "Дни календаря"
    column_list = [DayInfo.id, DayInfo.date, DayInfo.moon_day]
    column_searchable_list = [DayInfo.date, DayInfo.moon_day]
