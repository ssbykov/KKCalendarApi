from typing import Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserRepository:
    _instance: Optional["UserRepository"] = None

    def __new__(cls, session: AsyncSession) -> "UserRepository":
        if cls._instance is None:
            cls._instance = super(UserRepository, cls).__new__(cls)
            cls._instance.session = session
        return cls._instance

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_db(self):
        return SQLAlchemyUserDatabase(self.session, User)
