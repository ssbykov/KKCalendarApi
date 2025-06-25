from markupsafe import Markup
from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.model_views.event_photo import photo_url
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
    icon = "fa-solid fa-person"

    column_list = ("name",)
    column_details_exclude_list = (
        "id",
        "photo_id",
    )
    column_labels = {
        "name": "Имя",
        "caption": "Сообщение",
        "image": "Изображение",
    }
    can_edit = True
    can_delete = True
    can_export = False

    column_formatters_detail = {
        Advertisement.image: lambda model, _: (
            Markup(photo_url(model.image.photo_data))
            if hasattr(model, "image") and model.image
            else ""
        ),
    }

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
