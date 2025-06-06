from celery import chain  # type: ignore
from sqladmin import action
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.celery_worker import check_job_status, redis_client
from app.database import DayInfo
from app.database.crud.days_info import DayInfoRepository
from app.tasks.calendar_parser import parser_task, run_process_parser
from app.tasks import run_process_backup


class DayInfoAdmin(
    CustomModelView[DayInfo],
    model=DayInfo,
):
    repo_type = DayInfoRepository
    name_plural = "Дни календаря"
    name = "Информация по дню"
    icon = "fa-solid fa-calendar-days"

    column_labels = {
        "date": "Дата",
        "moon_day": "Лунный день",
        "elements": "Элементы",
        "la": "Энергия Ла",
        "haircutting": "Стрижка",
        "arch": "Световая арка",
        "yelam": "Йелам",
        "events": "События дня",
    }
    column_list = ("date", "events", "moon_day")
    page_size = 25
    column_searchable_list = ["date", "moon_day"]
    column_details_list = (
        "date",
        "moon_day",
        "elements",
        "la",
        "haircutting",
        "arch",
        "yelam",
        "events",
    )
    column_default_sort = ("date", True)
    column_sortable_list = ("date",)

    can_create = False
    can_delete = False
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)

    @action(
        name="load_new_data",
        label="Загрузить данные",
        add_in_detail=False,
        add_in_list=True,
        confirmation_message=f"Перед выполнением действия будет создана резервная копия базы данных. Продолжить?",
    )
    async def update_db(self, request: Request) -> RedirectResponse:
        task = check_job_status(parser_task.name)

        if task and task.status == "SUCCESS" or not task:
            backup_task = run_process_backup.s()
            new_parser_task = run_process_parser.si(period=12, update=True)
            result = chain(backup_task, new_parser_task)()
            redis_client.set(run_process_parser.name, result.id)

        request.session["flash_messages"] = self.get_update_status()
        return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    @staticmethod
    def get_update_status() -> str | None:
        name = parser_task.name
        task = check_job_status(name)
        if not task:
            return None
        status = task.status
        status_dict = {
            "PENDING": "Идет обновление...",
            "FAILURE": f"Ошибка: {type(getattr(task, 'result', None))}, {status}",
            "SUCCESS": f"Результат последнего обновления: {task.result}",
        }

        if status == "SUCCESS":
            redis_client.delete(name)

        return status_dict.get(status)
