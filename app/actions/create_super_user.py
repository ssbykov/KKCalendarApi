from typing import TYPE_CHECKING

from api.dependencies.user_manager_helper import user_manager_helper
from database.schemas.user import UserCreate

if TYPE_CHECKING:
    from pydantic import EmailStr


async def create_superuser(
    email: "EmailStr",
    password: str,
    is_active: bool = True,
    is_superuser: bool = True,
    is_verified: bool = True,
) -> None:
    user_create = UserCreate(
        email=email,
        password=password,
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
    )
    await user_manager_helper.create_user(user_create=user_create)
