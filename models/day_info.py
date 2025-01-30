from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from database.database import Base
from models.init_data import ELEMENTS, LA, ARCHES, YELAM, HAIRCUTTING_DAYS


class DayInfo(Base):
    __tablename__ = "day_info"

    date: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    moon_day: Mapped[str] = mapped_column(String(15), nullable=False)
    first_element_id: Mapped[int] = mapped_column(
        ForeignKey("elements.id"), nullable=False
    )
    first_element = relationship(
        "ElementModel",
        foreign_keys=[first_element_id],
        backref=backref("first_element", lazy="dynamic"),
    )
    second_element_id: Mapped[int] = mapped_column(
        ForeignKey("elements.id"), nullable=False
    )
    second_element = relationship(
        "ElementModel",
        foreign_keys=[second_element_id],
        backref=backref("second_element", lazy="dynamic"),
    )
    arch_id: Mapped[int] = mapped_column(ForeignKey("arch.id"), nullable=False)
    arch = relationship("ArchModel", backref=backref("arch", lazy="dynamic"))
    la_id: Mapped[int] = mapped_column(ForeignKey("la.id"), nullable=False)
    la = relationship("LaModel", backref=backref("la", lazy="dynamic"))
    yelam_id: Mapped[int] = mapped_column(ForeignKey("yelam.id"), nullable=False)
    yelam = relationship("YelamModel", backref=backref("yelam", lazy="dynamic"))
    haircutting_id: Mapped[int] = mapped_column(
        ForeignKey("haircutting.id"), nullable=False
    )
    haircutting = relationship(
        "HaircuttingModel", backref=backref("haircutting", lazy="dynamic")
    )
    descriptions: Mapped[list["DescriptionModel"]] = relationship(
        "DescriptionModel", back_populates="day_info", cascade="all, delete-orphan"
    )


class ElementModel(Base):
    init_data = ELEMENTS
    __tablename__ = "elements"
    name: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)


class LaModel(Base):
    init_data = LA

    __tablename__ = "la"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(100), nullable=False)


class ArchModel(Base):
    init_data = ARCHES

    __tablename__ = "arch"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    en_desc: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_desc: Mapped[str] = mapped_column(String(100), nullable=False)


class YelamModel(Base):
    init_data = YELAM
    __tablename__ = "yelam"
    month: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(30), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(30), nullable=False)


class HaircuttingModel(Base):
    init_data = HAIRCUTTING_DAYS
    __tablename__ = "haircutting"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_inauspicious: Mapped[bool] = mapped_column(nullable=False)


class DescriptionModel(Base):
    __tablename__ = "descriptions"

    text: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=True)
    day_info_id: Mapped[int] = mapped_column(
        ForeignKey("day_info.id", ondelete="CASCADE"), nullable=False
    )
    day_info: Mapped[DayInfo] = relationship("DayInfo", back_populates="descriptions")
