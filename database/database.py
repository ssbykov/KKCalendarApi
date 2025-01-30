from typing import Any

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    init_data: list[dict[str, Any]] = []
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
