from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from . import BaseWithId


class Lama(BaseWithId):
    """
    Модель для представления записи "Лама" в базе данных.

    Атрибуты:
        id: Уникальный идентификатор (наследуется от BaseWithId).
        name: Название ламы. Обязательное поле, максимальная длина — 200 символов. Уникальное значение.
        description: Описание ламы. Необязательное поле, может быть текстом произвольной длины.
        photo_id: Идентификатор связанной фотографии из таблицы `event_photos`. Может быть null.
        photo: Связь с моделью `EventPhoto`. Отношение "один к одному", обратная связь не настраивается.
    """

    __tablename__ = "lamas"
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("event_photos.id"), nullable=True, unique=True
    )
    photo = relationship(
        "EventPhoto", uselist=False, back_populates=None, viewonly=True
    )

    def __str__(self) -> str:
        return self.name
