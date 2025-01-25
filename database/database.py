from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    init_data: list[dict[str, Any]] = []
