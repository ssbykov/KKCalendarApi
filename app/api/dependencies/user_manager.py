from fastapi import Depends

from core.auth.user_manager import UserManager
from database.models import User


async def get_user_manager(user_db=Depends(User.get_db)):
    yield UserManager(user_db)
