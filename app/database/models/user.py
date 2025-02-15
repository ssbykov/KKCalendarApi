from datetime import datetime
from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseWithId

if TYPE_CHECKING:
    from database.db import SessionDep


class User(BaseWithId, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "users"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    @classmethod
    def get_db(cls, session: "SessionDep"):  # type: ignore
        return SQLAlchemyUserDatabase(session, cls)
