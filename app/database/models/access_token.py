from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

if TYPE_CHECKING:
    from database.db import SessionDep


class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Base):
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    @classmethod
    def get_db(cls, session: "SessionDep"):
        yield SQLAlchemyAccessTokenDatabase(session, cls)
