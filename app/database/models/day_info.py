from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from .base import BaseWithId
from .init_data import ELEMENTS, LA, ARCHES, YELAM, HAIRCUTTING_DAYS
from .mixines import ToDictMixin

if TYPE_CHECKING:
    from .event import Event, DayInfoEvent


class DayInfo(BaseWithId, ToDictMixin):
    ToDictMixin._exclude_params.append("id")

    __tablename__ = "day_info"

    date: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    moon_day: Mapped[str] = mapped_column(String(15), nullable=False)
    elements_id: Mapped[int] = mapped_column(ForeignKey("elements.id"), nullable=False)
    elements = relationship(
        "Elements",
        foreign_keys=[elements_id],
        backref=backref("elements", lazy="dynamic"),
    )
    arch_id: Mapped[int] = mapped_column(
        ForeignKey("skylight_arches.id"), nullable=False
    )
    arch = relationship("SkylightArch", backref=backref("arch", lazy="dynamic"))
    la_id: Mapped[int] = mapped_column(ForeignKey("la_positions.id"), nullable=False)
    la = relationship("LaPosition", backref=backref("la", lazy="dynamic"))
    yelam_id: Mapped[int] = mapped_column(ForeignKey("yelam.id"), nullable=False)
    yelam = relationship("Yelam", backref=backref("yelam", lazy="dynamic"))
    haircutting_id: Mapped[int] = mapped_column(
        ForeignKey("haircutting_days.id"), nullable=False
    )
    haircutting = relationship(
        "HaircuttingDay", backref=backref("haircutting", lazy="dynamic")
    )
    events: Mapped[list["Event"]] = relationship(
        "Event",
        secondary="dayinfo_events",
        back_populates="days",
    )

    def __str__(self) -> str:
        return f"Дата: {self.date}, лунный день {self.moon_day}, id: {self.id}"


class Elements(BaseWithId):
    init_data = ELEMENTS
    __tablename__ = "elements"
    en_name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    ru_name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    ru_text: Mapped[str] = mapped_column(Text, nullable=True)
    en_text: Mapped[str] = mapped_column(Text, nullable=True)
    is_positive: Mapped[bool] = mapped_column(nullable=False)

    def __str__(self) -> str:
        return self.ru_name


class LaPosition(BaseWithId):
    init_data = LA

    __tablename__ = "la_positions"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __str__(self) -> str:
        return self.ru_name


class SkylightArch(BaseWithId):
    init_data = ARCHES

    __tablename__ = "skylight_arches"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    en_desc: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_desc: Mapped[str] = mapped_column(String(100), nullable=False)

    def __str__(self) -> str:
        return self.ru_desc


class Yelam(BaseWithId):
    init_data = YELAM
    __tablename__ = "yelam"
    month: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(30), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(30), nullable=False)

    def __str__(self) -> str:
        return self.ru_name


class HaircuttingDay(BaseWithId):
    init_data = HAIRCUTTING_DAYS
    __tablename__ = "haircutting_days"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_inauspicious: Mapped[bool] = mapped_column(nullable=False)

    def __str__(self) -> str:
        return self.ru_name
