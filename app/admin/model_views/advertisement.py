from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.database import Advertisement
from app.database.crud.advertisements import AdvertisementRepository


class AdvertisementAdmin(
    CustomModelView[Advertisement],
    model=Advertisement,
):
    repo_type = AdvertisementRepository
    name_plural = "Сообщения"
    name = "Сообщение"
    icon = "fa-solid fa-message"
    category = "Сообщения бота"

    column_list = ("name",)
    column_details_exclude_list = (
        "id",
        "image_id",
    )
    column_labels = {
        "name": "Имя",
        "caption": "Сообщение",
        "image": "Изображение",
        "ids": "ID каналов",
        "schedules": "Расписания",
    }
    can_edit = True
    can_delete = True
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
