from typing import Any

from markupsafe import Markup
from sqladmin import ModelView
from sqlalchemy import Select, select, func
from sqlalchemy.orm import selectinload
from starlette.requests import Request

from admin.mixines import CustomNavMixin
from admin.model_views.event_photo import photo_url
from admin.utils import text_formater
from crud.events import EventRepository
from database import Event, db_helper


class EventAdmin(
    ModelView,
    CustomNavMixin[Event],
    model=Event,
):
    repo_type = EventRepository
    name_plural = "События"
    name = "Событие"
    icon = "fa-solid fa-calendar-plus"
    category = "Раздел событий"

    form_create_rules = [
        "days",
        "moon_day",
        "name",
        "en_name",
        "en_text",
        "ru_name",
        "ru_text",
        "link",
        "photo",
        "type",
        "emoji",
    ]
    form_edit_rules = form_create_rules.copy()

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
        "photo": "Фото события",
        "type": "Тип события",
        "emoji": "Эмодзи",
    }

    column_list = ["id", "ru_name", "emoji", "type"]
    column_searchable_list = ["en_name", "ru_name"]
    column_sortable_list = ["id"]
    column_formatters_detail = {
        Event.link: lambda model, attribute: getattr(model, "link", None)
        and Markup(
            f'<a href="{getattr(model, "link", "#")}" target="_blank">{getattr(model, "link", "No URL")}</a>'
        )
        or "",
        Event.photo: lambda model, _: (
            Markup(photo_url(model.photo.photo_data))
            if hasattr(model, "photo") and model.photo
            else ""
        ),
    } | text_formater(Event)

    detail_columns_counts = {
        "days": {"count": 4, "width": 200},
    }

    can_export = False

    column_details_exclude_list = [
        Event.id,
        Event.user_id,
        Event.photo_id,
        Event.type_id,
        Event.emoji_id,
    ]

    form_ajax_refs = {
        "days": {
            "fields": ("date",),
            "order_by": "date",
        },
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

    async def get_event(self, request: Request) -> Any:
        stmt = self._stmt_by_identifier(request.query_params["pks"])
        for relation in self._form_relations:
            stmt = stmt.options(selectinload(relation))
        return await self._get_object_by_pk(stmt)

    async def get_event_by_name(self, name: str) -> Event | None:
        async for session in db_helper.get_session():
            repo = self.repo_type(session)
            return await repo.get_event_by_name(name)
        return None

    async def check_unique(self, name: str, pk: int | str) -> bool:
        event = await self.get_event_by_name(name)
        return not event or event.id == int(pk)

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
