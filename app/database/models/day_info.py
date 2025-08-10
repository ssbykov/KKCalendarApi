from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from .base import BaseWithId
from .init_data import ELEMENTS, LA, ARCHES, YELAM, HAIRCUTTING_DAYS
from .mixines import ToDictMixin

if TYPE_CHECKING:
    from .event import Event


class DayInfo(BaseWithId, ToDictMixin):
    """
    Модель для хранения полной информации о календарных днях.

    Содержит астрологическую и эзотерическую информацию для каждого дня,
    включая лунный день, элементы, арки света, позиции LA, Yelam и
    рекомендации по стрижке волос. Используется для построения календаря
    с детальной информацией о каждом дне.

    Attributes:
        date (str): Дата в формате строки (YYYY-MM-DD).
        moon_day (str): Лунный день (до 15 символов).
        elements_id (int): ID элемента из таблицы elements.
        elements: Связь с моделью Elements.
        arch_id (int): ID арки света из таблицы skylight_arches.
        arch: Связь с моделью SkylightArch.
        la_id (int): ID позиции LA из таблицы la_positions.
        la: Связь с моделью LaPosition.
        yelam_id (int): ID Yelam из таблицы yelam.
        yelam: Связь с моделью Yelam.
        haircutting_id (int): ID дня стрижки из таблицы haircutting_days.
        haircutting: Связь с моделью HaircuttingDay.
    """

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
        return f"{self.date} - {self.moon_day}"

    @staticmethod
    def get_past_days_ids(days: list["DayInfo"]) -> list[str]:
        return sorted(
            str(day.id)
            for day in days
            if datetime.strptime(day.date, "%Y-%m-%d") <= datetime.now()
        )


class Elements(BaseWithId):
    """
    Модель для хранения информации о стихиях (элементах).

    Каждый элемент имеет уникальное название на русском и английском языках,
    а также текстовые описания. Элементы используются в DayInfo для указания
    энергетической составляющей дня.

    Attributes:
        en_name: Название элемента на английском языке.
        ru_name: Название элемента на русском языке.
        ru_text: Описание элемента на русском языке.
        en_text: Описание элемента на английском языке.
        is_positive: Флаг, указывающий, является ли элемент положительным.
    """

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
    """
    Модель для хранения информации о позиции LA (Light Aspect).

    Позиция LA связана с лунным днём и содержит описание на английском и русском языках.
    Используется в DayInfo для определения астрологического состояния дня.

    Attributes:
        moon_day: Лунный день, к которому относится эта позиция.
        en_name: Название позиции LA на английском языке.
        ru_name: Название позиции LA на русском языке.
    """

    init_data = LA

    __tablename__ = "la_positions"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __str__(self) -> str:
        return self.ru_name


class SkylightArch(BaseWithId):
    """
    Модель для хранения информации о арках света (Skylight Arch).

    Арки света связаны с лунными днями и содержат краткое описание на английском
    и русском языках. Они используются в DayInfo для характеристики дня.

    Attributes:
        moon_day: Лунный день, к которому относится арка света.
        name: Название арки света.
        en_desc: Описание арки на английском языке.
        ru_desc: Описание арки на русском языке.
    """

    init_data = ARCHES

    __tablename__ = "skylight_arches"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    en_desc: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_desc: Mapped[str] = mapped_column(String(100), nullable=False)

    def __str__(self) -> str:
        return self.ru_desc


class Yelam(BaseWithId):
    """
    Модель для хранения информации о Yelam (Эзотерический месяц).

    Yelam соответствует конкретному календарному месяцу и имеет названия на
    английском и русском языках. Используется в DayInfo для отслеживания
    эзотерических характеристик месяцев.

    Attributes:
        month: Номер месяца (от 1 до 12).
        en_name: Название Yelam на английском языке.
        ru_name: Название Yelam на русском языке.
    """

    init_data = YELAM
    __tablename__ = "yelam"
    month: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(30), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(30), nullable=False)

    def __str__(self) -> str:
        return self.ru_name


class HaircuttingDay(BaseWithId):
    """
    Модель для хранения информации о днях стрижки волос.

    Каждый день связан с лунным днём и имеет название на английском и русском языках.
    Также указывается, благоприятен ли день для стрижки.

    Attributes:
        moon_day: Лунный день.
        en_name: Название дня стрижки на английском языке.
        ru_name: Название дня стрижки на русском языке.
        is_inauspicious: Признак того, что день не рекомендуется для стрижки.
    """

    init_data = HAIRCUTTING_DAYS
    __tablename__ = "haircutting_days"
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_inauspicious: Mapped[bool] = mapped_column(nullable=False)

    def __str__(self) -> str:
        return self.ru_name
