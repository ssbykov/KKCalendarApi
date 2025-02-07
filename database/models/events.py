from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.mixines import ToDictMixin
from . import Base

if TYPE_CHECKING:
    from .day_info import DayInfo


class Events(Base, ToDictMixin):
    ToDictMixin._exclude_params.append("day_info_id")
    __tablename__ = "events"

    name: Mapped[str] = mapped_column(nullable=False)
    moon_day: Mapped[str] = mapped_column(String(10), nullable=True)
    en_name: Mapped[str] = mapped_column(nullable=False)
    ru_name: Mapped[str] = mapped_column(nullable=True)
    ru_text: Mapped[str] = mapped_column(Text, nullable=True)
    en_text: Mapped[str] = mapped_column(Text, nullable=True)
    link: Mapped[str] = mapped_column(nullable=True)
    # Связь через промежуточную модель
    event_links: Mapped[list["DayInfoEvent"]] = relationship(
        "DayInfoEvent", back_populates="event"
    )
    days: Mapped[list["DayInfo"]] = relationship(
        "DayInfo",
        secondary="dayinfo_events",  # Используем название таблицы
        back_populates="events",
    )


class DayInfoEvent(Base):
    """Промежуточная таблица для связи многие ко многим между DayInfo и Events."""

    __tablename__ = "dayinfo_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    day_info_id: Mapped[int] = mapped_column(ForeignKey("day_info.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)

    # Опциональные связи для удобства
    day_info: Mapped["DayInfo"] = relationship(
        "DayInfo", back_populates="dayinfo_links"
    )
    event: Mapped["Events"] = relationship("Events", back_populates="event_links")
