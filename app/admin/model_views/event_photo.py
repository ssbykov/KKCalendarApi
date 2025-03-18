from pathlib import Path
from typing import Any

from fastapi_storages import StorageImage
from markupsafe import Markup
from sqladmin import ModelView
from starlette.requests import Request

from admin.mixines import ActionNextBackMixin, CommonActionsMixin
from core import settings
from crud.event_photos import EventPhotoRepository
from database.models import EventPhoto


class EventPhotoAdmin(
    ModelView,
    ActionNextBackMixin[EventPhoto],
    CommonActionsMixin[EventPhoto],
    model=EventPhoto,
):
    repo_type = EventPhotoRepository
    name_plural = "Фотографии для событий"
    name = "Фото события"
    can_edit = True
    can_delete = True
    can_export = False

    column_labels = {
        "name": "Название",
        "photo_data": "Файл",
    }
    column_list = [EventPhoto.name]
    column_details_list = [EventPhoto.name, EventPhoto.photo_data]

    column_formatters_detail = {
        "photo_data": lambda model, _: (
            Markup(photo_url(model.photo_data)) if hasattr(model, "photo_data") else ""
        ),
    }

    async def after_model_delete(self, model: Any, request: Request) -> None:
        Path(model.photo_data).unlink()

    def is_visible(self, request: Request) -> bool:
        return self.is_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return self.is_superuser(request)


def photo_url(model: StorageImage) -> str:
    ratio = 100 / max(model.width, model.height)
    return (
        f'<img src="/{model.lstrip(settings.image_storage.root)}" '
        f"width={model.width * ratio} height={model.height * ratio}>"
    )
