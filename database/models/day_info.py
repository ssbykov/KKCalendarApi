from typing import Any

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from .base import Base
from .init_data import ELEMENTS, LA, ARCHES, YELAM, HAIRCUTTING_DAYS


class DayInfo(Base):
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
    descriptions: Mapped[list["Description"]] = relationship(
        "Description", back_populates="day_info", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        return to_dict(self, ["id", "_sa_instance_state"])


class Elements(Base):
    init_data = ELEMENTS
    __tablename__ = "elements"
    en_name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    ru_name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    ru_text: Mapped[str] = mapped_column(Text, nullable=True)
    en_text: Mapped[str] = mapped_column(Text, nullable=True)
    is_positive: Mapped[bool] = mapped_column(nullable=False)


class LaPosition(Base):
    init_data = LA

    __tablename__ = "la_positions"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(100), nullable=False)


class SkylightArch(Base):
    init_data = ARCHES

    __tablename__ = "skylight_arches"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    en_desc: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_desc: Mapped[str] = mapped_column(String(100), nullable=False)


class Yelam(Base):
    init_data = YELAM
    __tablename__ = "yelam"
    month: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(30), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(30), nullable=False)


class HaircuttingDay(Base):
    init_data = HAIRCUTTING_DAYS
    __tablename__ = "haircutting_days"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_inauspicious: Mapped[bool] = mapped_column(nullable=False)


class SpecialDay(Base):
    __tablename__ = "specialdays"
    moon_days: Mapped[str] = mapped_column(String(10), nullable=True)
    en_name: Mapped[str] = mapped_column(nullable=False)
    ru_name: Mapped[str] = mapped_column(nullable=True)
    ru_text: Mapped[str] = mapped_column(Text, nullable=True)
    en_text: Mapped[str] = mapped_column(Text, nullable=True)


class Description(Base):
    __tablename__ = "descriptions"

    en_name: Mapped[str] = mapped_column(nullable=False)
    ru_name: Mapped[str] = mapped_column(nullable=True)
    ru_text: Mapped[str] = mapped_column(Text, nullable=True)
    en_text: Mapped[str] = mapped_column(Text, nullable=True)
    link: Mapped[str] = mapped_column(nullable=True)
    day_info_id: Mapped[int] = mapped_column(
        ForeignKey("day_info.id", ondelete="CASCADE"), nullable=False
    )
    day_info: Mapped[DayInfo] = relationship("DayInfo", back_populates="descriptions")

    def to_dict(self) -> dict[str, str]:
        return to_dict(self, ["id", "day_info_id", "_sa_instance_state"])


def to_dict(obj: Base, exclude_params: list[str]) -> dict[str, Any]:
    data_dict = {k: v for k, v in obj.__dict__.items() if k not in exclude_params}
    return data_dict
