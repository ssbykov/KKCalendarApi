from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from .base import Base
from .init_data import ELEMENTS, LA, ARCHES, YELAM, HAIRCUTTING_DAYS


class DayInfo(Base):
    __tablename__ = "day_info"

    date: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    moon_day: Mapped[str] = mapped_column(String(15), nullable=False)
    first_element_id: Mapped[int] = mapped_column(
        ForeignKey("elements.id"), nullable=False
    )
    first_element = relationship(
        "Element",
        foreign_keys=[first_element_id],
        backref=backref("first_element", lazy="dynamic"),
    )
    second_element_id: Mapped[int] = mapped_column(
        ForeignKey("elements.id"), nullable=False
    )
    second_element = relationship(
        "Element",
        foreign_keys=[second_element_id],
        backref=backref("second_element", lazy="dynamic"),
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


class Element(Base):
    init_data = ELEMENTS
    __tablename__ = "elements"
    name: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)


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


class Description(Base):
    __tablename__ = "descriptions"

    text: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=True)
    day_info_id: Mapped[int] = mapped_column(
        ForeignKey("day_info.id", ondelete="CASCADE"), nullable=False
    )
    day_info: Mapped[DayInfo] = relationship("DayInfo", back_populates="descriptions")
