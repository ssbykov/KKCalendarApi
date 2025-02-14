from typing import Any

from sqladmin import Admin

from .model_views import EventAdmin, DayInfoAdmin
from app.core.config import settings
from app.database import db_helper


def init_admin(app: Any) -> None:
    admin = Admin(app, db_helper.engine, templates_dir=settings.sql_admin.templates_dir)
    admin.add_view(DayInfoAdmin)
    admin.add_view(EventAdmin)
