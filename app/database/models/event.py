from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from . import BaseWithId
from .init_data import EVENTS
from .mixines import ToDictMixin

if TYPE_CHECKING:
    from .day_info import DayInfo


class Event(BaseWithId, ToDictMixin):
    init_data = EVENTS

    __tablename__ = "events"

    name: Mapped[str] = mapped_column(nullable=False)
    moon_day: Mapped[str] = mapped_column(String(10), nullable=True)
    en_name: Mapped[str] = mapped_column(nullable=False)
    ru_name: Mapped[str] = mapped_column(nullable=False)
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
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    user = relationship("User", backref=backref("user", lazy="dynamic"))

    def __str__(self) -> str:
        return self.ru_name


class DayInfoEvent(BaseWithId):
    """Промежуточная таблица для связи многие ко многим между DayInfo и Event."""

    __tablename__ = "dayinfo_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    day_info_id: Mapped[int] = mapped_column(ForeignKey("day_info.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
