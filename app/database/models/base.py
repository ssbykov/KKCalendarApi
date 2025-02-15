from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from core import settings


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.naming_convention)

    init_data: list[dict[str, Any]] = []
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
