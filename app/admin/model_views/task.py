from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.database import TaskScheduler
from app.database.crud.tasks import TaskRepository


class TaskAdmin(
    CustomModelView[TaskScheduler],
    model=TaskScheduler,
):
    repo_type = TaskRepository
    name_plural = "Задания"
    name = "Задание"
    icon = "fa-solid fa-solid fa-calendar-week"

    category = "Сообщения бота"
    column_exclude_list = ("id",)
    column_labels = {
        "advertisement": "Сообщение",
        "hour": "Часы",
        "minute": "Минуты",
        "days": "Дни недели",
        "timezone": "Зона",
    }

    column_details_exclude_list = ("advertisement_id", "id")

    can_edit = True
    can_delete = True
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
