from datetime import datetime
from typing import TYPE_CHECKING, Any

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseWithId

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(BaseWithId, SQLAlchemyBaseUserTable[int]):  # type: ignore[misc]
    __tablename__ = "users"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        default=func.now(),
        server_default=func.now(),
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):  # type: ignore
        return SQLAlchemyUserDatabase(session, cls)

    def __str__(self) -> str:
        return self.email

    def model_dump(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "is_verified": self.is_verified,
        }
