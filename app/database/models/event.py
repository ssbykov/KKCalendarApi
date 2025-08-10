from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from . import BaseWithId
from .init_data import EVENTS
from .mixines import ToDictMixin

if TYPE_CHECKING:
    from .day_info import DayInfo


class Event(BaseWithId, ToDictMixin):
    init_data = EVENTS

    __tablename__ = "events"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    moon_day: Mapped[str] = mapped_column(String(20), nullable=True)
    en_name: Mapped[str] = mapped_column(nullable=False)
    ru_name: Mapped[str] = mapped_column(nullable=False)
    en_text: Mapped[str] = mapped_column(Text, nullable=True)
    ru_text: Mapped[str] = mapped_column(Text, nullable=True)
    link: Mapped[str] = mapped_column(nullable=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("event_photos.id"), nullable=True)
    photo = relationship("EventPhoto", backref=backref("event"))
    type_id: Mapped[int] = mapped_column(ForeignKey("event_types.id"), nullable=True)
    type = relationship("EventType", backref=backref("events"))
    emoji_id: Mapped[int] = mapped_column(ForeignKey("emoji.id"), nullable=True)
    emoji = relationship("Emoji", backref=backref("events"))
    days: Mapped[list["DayInfo"]] = relationship(
        "DayInfo",
        secondary="dayinfo_events",
        order_by="DayInfo.date",
        back_populates="events",
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    user = relationship("User", backref=backref("user", lazy="select"))

    def __str__(self) -> str:
        return self.ru_name


class EventType(BaseWithId):
    """
    The name of the database table backing this class.

    This is set by the `__tablename__` attribute, and is used by SQLAlchemy to
    locate the table in the database.
    """
    __tablename__ = "event_types"
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    desc: Mapped[str] = mapped_column(String(100), nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    def __str__(self) -> str:
        return self.name


class DayInfoEvent(BaseWithId):
    """Промежуточная таблица для связи многие ко многим между DayInfo и Event."""

    __tablename__ = "dayinfo_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    day_info_id: Mapped[int] = mapped_column(ForeignKey("day_info.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
