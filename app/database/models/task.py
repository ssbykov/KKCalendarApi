from sqlalchemy import Text, ForeignKey, Integer, String, CheckConstraint, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import BaseWithId


class TaskScheduler(BaseWithId):
    """
    Модель для хранения расписания задач (например, автоматической публикации объявления).

    Атрибуты:
        id: Уникальный идентификатор (наследуется от BaseWithId).
        advertisement_id: Идентификатор связанного объявления. Обязательное поле.
        hour: Час выполнения задачи (0-23). По умолчанию 0.
        minute: Минута выполнения задачи (0-59). По умолчанию 0.
        days: Список дней недели, разделённых запятыми. По умолчанию — все дни.
        timezone: Временная зона для расписания. По умолчанию — Europe/Moscow.
        is_active: Флаг активности расписания. По умолчанию True.
        advertisement: Связь с моделью Advertisement. Отношение "многие к одному".

    Ограничения:
        - Проверка диапазона часов (0–23).
        - Проверка диапазона минут (0–59).
    """

    __tablename__ = "task_schedulers"
    __table_args__ = (
        CheckConstraint("hour >= 0 AND hour <= 23", name="check_hour_range"),
        CheckConstraint("minute >= 0 AND minute <= 59", name="check_minute_range"),
    )
    advertisement_id: Mapped[int] = mapped_column(
        ForeignKey("advertisements.id", ondelete="CASCADE"), nullable=False
    )
    hour: Mapped[int] = mapped_column(Integer, default=0)
    minute: Mapped[int] = mapped_column(Integer, default=0)
    days: Mapped[str] = mapped_column(
        String(50),
        default="mon,tue,wed,thu,fri,sat,sun",
        comment="Comma-separated list of weekdays",
    )
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Moscow")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    advertisement = relationship("Advertisement", backref="schedules")

    def __str__(self) -> str:
        return f"Время: {self.hour}:{self.minute:02d}, {self.days}"


class Advertisement(BaseWithId):
    """
    Модель для хранения информации о сообщении.

    Атрибуты:
        id: Уникальный идентификатор (наследуется от BaseWithId).
        name: Название объявления. Обязательное поле.
        image_id: Идентификатор связанной фотографии. Может быть null.
        image: Связь с моделью EventPhoto. Отношение "один к одному".
        caption: Описание или подпись к объявлению. Необязательное поле.
        ids: Дополнительные идентификаторы в формате JSON. Например, ID в соцсетях.
        schedules: Связанные расписания (через обратную ссылку из TaskScheduler).
    """

    __tablename__ = "advertisements"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    image_id: Mapped[int | None] = mapped_column(
        ForeignKey("event_photos.id", ondelete="SET NULL"), nullable=True
    )
    image = relationship(
        "EventPhoto", uselist=False, back_populates=None, viewonly=True
    )
    caption: Mapped[str] = mapped_column(Text)
    ids: Mapped[dict] = mapped_column(JSON)

    def __str__(self) -> str:
        return self.name
