from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core import settings
from . import BaseWithId


class EventPhoto(BaseWithId):
    __tablename__ = "event_photos"
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    photo_data: Mapped[str] = mapped_column(
        ImageType(
            storage=FileSystemStorage(
                path=settings.image_storage.root + settings.image_storage.storage
            )
        ),
        nullable=False,
    )
