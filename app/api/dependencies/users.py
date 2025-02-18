from typing import TYPE_CHECKING

from fastapi import Depends

from database.models import User

from database import SessionDep, db_helper

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_db(session: "AsyncSession" = Depends(db_helper.get_session)):
    yield User.get_db(session)
