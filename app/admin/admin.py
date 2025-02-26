from typing import Any

from sqladmin import Admin
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from core import settings
from database import db_helper
from .admin_auth import sql_admin_authentication_backend, AdminAuth
from .model_views import EventAdmin, DayInfoAdmin


def init_admin(app: Any) -> None:
    admin = NewAdmin(
        app,
        db_helper.engine,
        templates_dir=settings.sql_admin.templates,
        authentication_backend=sql_admin_authentication_backend,
    )
    admin.add_view(DayInfoAdmin)
    admin.add_view(EventAdmin)


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
