from typing import AsyncGenerator, TYPE_CHECKING

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from api.dependencies.users import get_user_db
from core.auth.user_manager import UserManager

if TYPE_CHECKING:
    from database.models import User


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase["User", int] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)
