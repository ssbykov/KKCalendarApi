from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi_users.exceptions import InvalidVerifyToken, UserAlreadyVerified

from api.dependencies.backend import authentication_backend
from core.config import settings
from database.schemas.user import UserRead, UserCreate
from utils.email_sender import send_verification_email
from .fastapi_users import fastapi_users
from ..dependencies.user_manager import get_user_manager

router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)

if TYPE_CHECKING:
    from core.auth.user_manager import UserManager


@router.get("/verify/")
async def verify_user(
    token: str, user_manager: "UserManager" = Depends(get_user_manager)
) -> str:
    try:
        user = await user_manager.verify(token=token)
        await send_verification_email(
            user_email=user.email,
            token=token,
            action="verify_confirmation",
        )
        return f"Пользователь {user.email} верифицирован."
    except InvalidVerifyToken:
        return "Невалидный токен"
    except UserAlreadyVerified:
        return "Пользователь уже верифицирован"


# login, logout
router.include_router(
    router=fastapi_users.get_auth_router(
        authentication_backend,
        requires_verification=True,
    ),
)

# register
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# verify
router.include_router(router=fastapi_users.get_verify_router(UserRead))

router.include_router(router=fastapi_users.get_reset_password_router())
