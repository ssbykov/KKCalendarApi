from sqladmin import ModelView
from starlette.requests import Request

from admin.utils import check_superuser
from crud.backup_db import BackupDbRepository
from database import db_helper
from database.models.backup_db import BackupDb


class BackupDbAdmin(
    ModelView,
    model=BackupDb,
):
    repo_type = BackupDbRepository
    name_plural = "Резервные копии"
    name = "Резервная копия"
    column_list = ["name"]
    column_labels = {
        "name": "Имя копии",
    }
    can_edit = False
    can_delete = True
    can_export = False
    can_view_details = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)

    async def get_by_id(self, backup_id: int) -> BackupDb | None:
        async for session in db_helper.get_session():
            repo = self.repo_type(session)
            return await repo.get_by_id(backup_id)
        return None
