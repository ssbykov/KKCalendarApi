from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.mixines import ToDictMixin
from . import Base
from .init_data import EVENTS

if TYPE_CHECKING:
    from .day_info import DayInfo


class Event(Base, ToDictMixin):
    init_data = EVENTS

    __tablename__ = "events"

    name: Mapped[str] = mapped_column(nullable=False)
    moon_day: Mapped[str] = mapped_column(String(10), nullable=True)
    en_name: Mapped[str] = mapped_column(nullable=False)
    ru_name: Mapped[str] = mapped_column(nullable=True)
    en_text: Mapped[str] = mapped_column(Text, nullable=True)
    ru_text: Mapped[str] = mapped_column(Text, nullable=True)
    link: Mapped[str] = mapped_column(nullable=True)
    is_mutable: Mapped[bool] = mapped_column(
        nullable=False, server_default="0", default=False
    )
    days: Mapped[list["DayInfo"]] = relationship(
        "DayInfo",
        secondary="dayinfo_events",
        back_populates="events",
    )

    def __str__(self):
        return self.ru_name


class DayInfoEvent(Base):
    """Промежуточная таблица для связи многие ко многим между DayInfo и Event."""

    __tablename__ = "dayinfo_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    day_info_id: Mapped[int] = mapped_column(ForeignKey("day_info.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
