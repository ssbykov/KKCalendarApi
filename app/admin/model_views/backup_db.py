from sqladmin import ModelView
from starlette.requests import Request

from admin.utils import check_superuser
from database.models.backup_db import BackupDb


class BackupDbAdmin(
    ModelView,
    model=BackupDb,
):
    name_plural = "Резервные копии"
    name = "Резервная копия"
    column_list = ["name"]
    column_labels = {
        "name": "Имя копии",
    }
    can_edit = False
    can_delete = True
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
