from typing import TYPE_CHECKING

from database.models import AccessToken

if TYPE_CHECKING:
    from database import SessionDep


async def get_access_token_db(session: "SessionDep"):
    yield AccessToken.get_db(session)
