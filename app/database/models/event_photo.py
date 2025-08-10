from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.custom_types import ImageType
from . import BaseWithId


class EventPhoto(BaseWithId):
    """
    Модель для хранения фотографий событий.
    
    Используется для сохранения изображений, связанных с календарными событиями.
    Каждая фотография имеет название и данные изображения в кодированном виде.
    
    Attributes:
        name (str): Название фотографии (до 30 символов).
        photo_data (str): Данные изображения в кодированном формате.
    """
    __tablename__ = "event_photos"
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    photo_data: Mapped[str] = mapped_column(
        ImageType(),
        nullable=False,
    )

    def __str__(self) -> str:
        return self.name
