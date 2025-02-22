from fastapi import APIRouter
from fastapi_users.exceptions import InvalidVerifyToken, UserAlreadyVerified

from api.dependencies.backend import authentication_backend
from api.dependencies.user_manager_helper import user_manager_helper
from core.config import settings
from database.schemas.user import UserRead, UserCreate
from utils.email_sender import send_verification_email
from .fastapi_users import fastapi_users

router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)


@router.get("/verify/")
async def verify_user(token: str):
    try:
        user = await user_manager_helper.verify(token=token)
        await send_verification_email(
            user_email=user.email,
            token=token,
            action="verify_confirmation",
        )
        return f"Пользователь {user.email} верифицирован."
    except InvalidVerifyToken as e:
        return "Невалидный токен"
    except UserAlreadyVerified as e:
        return "Пользователь уже верифицирован"


# login, logout
router.include_router(
    router=fastapi_users.get_auth_router(
        authentication_backend, requires_verification=True
    ),
)

# register
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# verify
router.include_router(
    router=fastapi_users.get_verify_router(UserRead),
)
