from typing import TYPE_CHECKING, Any

from fastapi import Depends

from database import db_helper
from database.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_db(session: "AsyncSession" = Depends(db_helper.get_session)) -> Any:
    yield User.get_db(session)
