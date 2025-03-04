from typing import Any, cast

from sqladmin import Admin
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from core import settings
from database import db_helper
from .backend import AdminAuth, owner_required
from .model_views import EventAdmin, DayInfoAdmin


async def init_admin(app: Any) -> None:
    admin = NewAdmin(
        app,
        db_helper.engine,
        title="Календарь событий",
        templates_dir=settings.sql_admin.templates,
        authentication_backend=AdminAuth(secret_key=settings.sql_admin.secret),
    )
    admin.add_view(DayInfoAdmin)
    admin.add_view(EventAdmin)
    assert isinstance(admin.authentication_backend, AdminAuth)
    await admin.authentication_backend.create_superuser()


class NewAdmin(Admin):
    async def login(self, request: Request) -> Response:
        assert isinstance(self.authentication_backend, AdminAuth)

        context: dict[str, str | None] = {}
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "sqladmin/login.html")

        response = await self.authentication_backend.login_with_info(request)
        if not response.is_ok:
            context["error"] = response.error
            context["message"] = response.message
            return await self.templates.TemplateResponse(
                request, "sqladmin/login.html", context, status_code=400
            )

        return RedirectResponse(request.url_for("admin:index"), status_code=302)

    @owner_required
    async def details(self, request: Request) -> Response:
        result = await super().details(request)
        return cast(Response, result)

    @owner_required
    async def edit(self, request: Request) -> Response:
        result = await super().edit(request)
        return cast(Response, result)

    @owner_required
    async def delete(self, request: Request) -> Response:
        result = await super().delete(request)
        return cast(Response, result)
