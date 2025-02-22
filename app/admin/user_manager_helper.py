import contextlib
from typing import TYPE_CHECKING

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication import JWTStrategy

from api.dependencies.user_manager import get_user_manager
from api.dependencies.users import get_user_db
from core import settings
from database import db_helper
from database.models import User
from database.schemas.user import UserCreate

get_async_session_context = contextlib.asynccontextmanager(db_helper.get_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

if TYPE_CHECKING:
    from core.auth.user_manager import UserManager
    from pydantic import EmailStr


def user_manager_decorator(func):
    async def wrapper(*args, **kwargs):
        # Создаем контексты для session и user_manager
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    # Передаем user_manager в целевой метод
                    result = await func(user_manager=user_manager, *args, **kwargs)
                    return result

    return wrapper


class UserManagerHelper:
    def __init__(
        self,
        default_email: "EmailStr",
        default_password: str,
        default_is_active=True,
        default_is_superuser=True,
        default_is_verified=True,
    ):
        self.default_is_active = default_is_active
        self.default_is_superuser = default_is_superuser
        self.default_is_verified = default_is_verified
        self.default_email = default_email
        self.default_password = default_password

    @staticmethod
    @user_manager_decorator
    async def create_user(
        user_manager: "UserManager",
        user_create: UserCreate,
    ) -> User:
        user = await user_manager.create(
            user_create=user_create,
            safe=False,
        )
        return user

    @staticmethod
    @user_manager_decorator
    async def get_access_token(
        user_manager: "UserManager",
        credentials: OAuth2PasswordRequestForm,
    ) -> str | None:
        if is_authenticated := await user_manager.authenticate(credentials):
            if is_authenticated.is_active and is_authenticated.is_verified:
                user = await user_manager.get_by_email(credentials.username)
                jwt_strategy = JWTStrategy(
                    secret=settings.sql_admin.jwt_secret,
                    lifetime_seconds=settings.access_token.lifetime_seconds,
                )
                access_token = await jwt_strategy.write_token(user)
                return access_token
            else:
                print("негодный юзер")
        else:
            print("неверный логин или пароль")

    async def create_superuser(self):
        user_create = UserCreate(
            email=self.default_email,
            password=self.default_password,
            is_active=self.default_is_active,
            is_superuser=self.default_is_superuser,
            is_verified=self.default_is_verified,
        )
        await self.create_user(user_create=user_create)


user_manager_helper = UserManagerHelper(
    default_email=settings.super_user.email,
    default_password=settings.super_user.email,
)
