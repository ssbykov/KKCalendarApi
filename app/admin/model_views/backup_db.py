import asyncio

from admin.utils import check_superuser
from crud.backup_db import BackupDbRepository
from database import db_helper
from database.backup_db import restore_database_from_dump
from database.models.backup_db import BackupDb
from sqladmin import ModelView, action
from starlette.requests import Request
from starlette.responses import RedirectResponse


class BackupDbAdmin(
    ModelView,
    model=BackupDb,
):
    repo_type = BackupDbRepository
    name_plural = "Резервные копии"
    name = "Резервная копия"
    icon = "fa-solid fa-box-archive"

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

    @action(
        name="restore",
        label="Восстановить",
        add_in_detail=False,
        add_in_list=True,
        confirmation_message=f"Вы уверены, что хотите восстановить базу из резервной копии?"
        f"Будет использоавана последная отмеченная резервная копия.",
    )
    async def restore_db(self, request: Request) -> RedirectResponse:
        async for session in db_helper.get_session():
            if backup_id := request.query_params.get("pks", "").split(",")[-1]:
                repo = self.repo_type(session)
                if backup := await repo.get_by_id(int(backup_id)):
                    asyncio.create_task(restore_database_from_dump(backup.name))
                    return RedirectResponse(url="/admin/logout")
        return RedirectResponse(request.url_for("admin:list", identity=self.identity))
