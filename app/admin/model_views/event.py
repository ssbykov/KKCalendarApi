from datetime import datetime
from typing import Any

from markupsafe import Markup
from sqladmin import ModelView
from sqlalchemy import Select, select, func
from starlette.requests import Request

from admin.mixines import ActionNextBackMixin, CommonActionsMixin
from crud.days_info import DayInfoRepository
from crud.events import EventRepository
from database import Event, db_helper


class EventAdmin(
    ModelView,
    ActionNextBackMixin[Event],
    CommonActionsMixin[Event],
    model=Event,
):
    repo_type = EventRepository
    name_plural = "События"
    name = "Событие"
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
        Event.link: lambda model, attribute: getattr(model, "link", None)
        and Markup(
            f'<a href="{getattr(model, "link", "#")}" target="_blank">{getattr(model, "link", "No URL")}</a>'
        )
        or "",
    }

    can_export = False

    column_details_exclude_list = [Event.id, Event.user_id, Event.is_mutable]

    form_ajax_refs = {
        "days": {
            "fields": ("date",),
            "order_by": "date",
        }
    }

    def list_query(self, request: Request) -> Select[Any]:
        stmt: Select[Any] = select(self.model)
        return self.get_query(request, stmt)

    def count_query(self, request: Request) -> Select[Any]:
        stmt: Select[Any] = select(func.count(self.pk_columns[0]))
        return self.get_query(request, stmt)

    def form_edit_query(self, request: Request) -> Select[Any]:
        if self.get_user_not_superuser(request):
            if "user" in self.form_edit_rules:
                self.form_edit_rules.remove("user")
        else:
            self.form_edit_rules.append("user")
        return super().form_edit_query(request)

    def get_query(self, request: Request, stmt: Select[Any]) -> Select[Any]:
        if user := self.get_user_not_superuser(request):
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
        data.setdefault("user", int(request.session.get("user", {}).get("id")))
        old_days = [
            day.id
            for day in model.days
            if datetime.strptime(day.date, "%Y-%m-%d") <= datetime.now()
        ]
        new_days = []
        for day_id in data.get("days", []):
            async for session in db_helper.get_session():
                repo = DayInfoRepository(session)
                day_info = await repo.get_day_by_id(day_id)
                if datetime.strptime(day_info.date, "%Y-%m-%d") > datetime.now():
                    new_days.append(day_id)

        data["days"] = new_days + old_days

    @staticmethod
    def get_user_not_superuser(request: Request) -> Any | None:
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
