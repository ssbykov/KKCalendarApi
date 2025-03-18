from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core import settings
from . import BaseWithId


class EventPhoto(BaseWithId):
    storage = FileSystemStorage(path=settings.image_storage.full_path)
    __tablename__ = "event_photos"
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    photo_data: Mapped[str] = mapped_column(
        ImageType(storage=storage),
        nullable=False,
    )
