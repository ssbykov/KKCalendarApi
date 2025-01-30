from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "users"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
