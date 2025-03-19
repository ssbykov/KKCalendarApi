from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.custom_types import ImageType
from . import BaseWithId


class EventPhoto(BaseWithId):
    __tablename__ = "event_photos"
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    photo_data: Mapped[str] = mapped_column(
        ImageType(),
        nullable=False,
    )

    def __str__(self) -> str:
        return self.name
