from typing import TYPE_CHECKING

from database.models import User

if TYPE_CHECKING:
    from database import SessionDep


async def get_user_db(session: "SessionDep"):
    yield User.get_db(session)
