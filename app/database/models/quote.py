from datetime import datetime

from sqlalchemy import Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from . import BaseWithId


class Quote(BaseWithId):
    """
    Модель для представления цитаты, связанной с ламой.

    Атрибуты:
        id: Уникальный идентификатор (наследуется от BaseWithId).
        text: Текст цитаты. Может быть пустым.
        lama_id: Идентификатор связанной ламы из таблицы `lamas`. Обязательное поле.
        lama: Связь с моделью `Lama`. Отношение "многие к одному".
        created_at: Дата и время создания записи. Устанавливается автоматически при вставке в БД.
    """

    __tablename__ = "quotes"
    text: Mapped[str] = mapped_column(Text, nullable=True)
    lama_id: Mapped[int] = mapped_column(ForeignKey("lamas.id"), nullable=False)
    lama = relationship("Lama", backref=backref("lama"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    def __str__(self) -> str:
        return self.text
