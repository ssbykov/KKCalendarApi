from typing import Any

from markupsafe import Markup
from sqladmin import ModelView
from sqlalchemy import Select, select, func
from starlette.requests import Request

from admin.mixines import ActionNextBackMixin
from crud.days_info import DayInfoRepository
from crud.events import EventRepository
from database import Event, DayInfo


class EventAdmin(ActionNextBackMixin, ModelView, model=Event):
    repo_type = EventRepository
    name_plural = "События"
    name = "Информация по событию"
    form_create_rules = [
        "days",
        "name",
        "en_name",
        "en_text",
        "ru_name",
        "ru_text",
        "link",
    ]
    form_edit_rules = [
        "days",
        "name",
        "en_name",
        "en_text",
        "ru_name",
        "ru_text",
        "link",
    ]

    column_labels = {
        "days": "Даты события",
        "name": "Название",
        "user": "Пользователь",
        "moon_day": "Лунные дни",
        "en_name": "Заголовок на английском",
        "en_text": "Описание на английском",
        "ru_name": "Заголовок на русском",
        "ru_text": "Описание на русском",
        "link": "Ссылка на событие",
    }

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
        Event.link: lambda model, attribute: getattr(model, "link", None)
        and Markup(
            f'<a href="{getattr(model, "link", "#")}" target="_blank">{getattr(model, "link", "No URL")}</a>'
        )
        or "",
    }

    column_details_exclude_list = [Event.id, Event.user_id, Event.is_mutable]

    def list_query(self, request: Request) -> Select[Any]:
        stmt: Select[Any] = select(self.model)
        return self.get_query(request, stmt)

    def count_query(self, request: Request) -> Select[Any]:
        stmt: Select[Any] = select(func.count(self.pk_columns[0]))
        return self.get_query(request, stmt)

    def form_edit_query(self, request: Request) -> Select[Any]:
        if self.get_user(request):
            if "user" in self.form_edit_rules:
                self.form_edit_rules.remove("user")
        else:
            self.form_edit_rules.append("user")
        return super().form_edit_query(request)

    def get_query(self, request: Request, stmt: Select[Any]) -> Select[Any]:
        if user := self.get_user(request):
            stmt = stmt.filter(Event.user_id == user.get("id"))
        return stmt

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: Any,
        is_created: bool,
        request: Request,
    ) -> None:
        data["link"] = self.ensure_http_prefix(data["link"])
        if user := self.get_user(request):
            data["user_id"] = user.get("id")

    @staticmethod
    def get_user(request: Request) -> Any | None:
        user = request.session.get("user")
        if isinstance(user, dict) and not user.get("is_superuser"):
            return user
        return None

    @staticmethod
    def ensure_http_prefix(url: str) -> str:
        if url and not (url.startswith("http://") or url.startswith("https://")):
            return f"http://{url}"
        return url


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
    can_create = False
    can_delete = False

    def is_visible(self, request: Request) -> bool:
        return self.is_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return self.is_superuser(request)

    @staticmethod
    def is_superuser(request: Request) -> bool:
        user = request.session.get("user")
        return isinstance(user, dict) and bool(user.get("is_superuser"))
