from fastapi import APIRouter

from api.dependencies.backend import authentication_backend
from database.schemas.user import UserRead, UserCreate
from .fastapi_users import fastapi_users
from core.config import settings

router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)

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
