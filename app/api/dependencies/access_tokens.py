from typing import TYPE_CHECKING

from fastapi import Depends

from database import db_helper
from database.models import AccessToken

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_access_token_db(
    session: "AsyncSession" = Depends(db_helper.get_session),
):
    yield AccessToken.get_db(session)
