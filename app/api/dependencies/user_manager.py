from fastapi import Depends

from api.dependencies.users import get_user_db
from core.auth.user_manager import UserManager


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
