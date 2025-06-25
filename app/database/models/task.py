from sqlalchemy import Text, ForeignKey, Integer, String, CheckConstraint, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import BaseWithId


class TaskScheduler(BaseWithId):
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

    advertisement = relationship("Advertisement", back_populates="schedules")


class Advertisement(BaseWithId):
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

    schedules = relationship("TaskScheduler", back_populates="advertisement")
