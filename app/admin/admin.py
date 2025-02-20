from typing import Any

from sqladmin import Admin

from .admin_auth import sql_admin_authentication_backend
from .model_views import EventAdmin, DayInfoAdmin
from core import settings
from database import db_helper


def init_admin(app: Any) -> None:
    admin = Admin(
        app,
        db_helper.engine,
        templates_dir=settings.sql_admin.templates,
        authentication_backend=sql_admin_authentication_backend,
    )
    admin.add_view(DayInfoAdmin)
    admin.add_view(EventAdmin)
