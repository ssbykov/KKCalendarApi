import logging
from pathlib import Path
from typing import Any, Dict

from fastapi_storages import StorageImage  # type: ignore
from markupsafe import Markup
from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.core import settings
from app.database.crud.event_photos import EventPhotoRepository
from app.database.models import EventPhoto


class EventPhotoAdmin(
    CustomModelView[EventPhoto],
    model=EventPhoto,
):
    repo_type = EventPhotoRepository
    name_plural = "Изображения"
    name = "Изображение"
    icon = "fa-solid fa-image"

    can_edit = True
    can_delete = True
    can_export = False

    column_labels = {
        "name": "Название",
        "photo_data": "Файл",
        "event": "События",
    }
    column_list = ("name",)
    column_searchable_list = ("name",)
    column_details_list = ("name", "photo_data")

    column_formatters_detail = {
        "photo_data": lambda model, _: (
            Markup(photo_url(model.photo_data)) if hasattr(model, "photo_data") else ""
        ),
    }

    form_ajax_refs = {
        "event": {
            "fields": ("ru_name",),
        }
    }

    async def on_model_change(
        self, data: Dict[str, Any], model: Any, is_created: bool, request: Request
    ) -> None:
        form = await request.form()

        if "photo_data" in form and not getattr(form["photo_data"], "size", 0):
            data.pop("photo_data", None)

        await super().on_model_change(data, model, is_created, request)

    async def after_model_delete(self, model: Any, request: Request) -> None:
        Path(model.photo_data).unlink()

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)


def photo_url(model: StorageImage) -> str | None:
    try:
        ratio = 100 / max(model.width, model.height)
        return (
            f'<img src="{model.removeprefix(settings.image_storage.root)}"'
            f"width={model.width * ratio} height={model.height * ratio}>"
        )
    except Exception as err:
        logging.error(f"Error: {err}")
        return None
