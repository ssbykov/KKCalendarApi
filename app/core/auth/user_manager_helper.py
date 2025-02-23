import contextlib
from functools import wraps
from typing import TYPE_CHECKING, Callable, Any

from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies.access_tokens import get_access_token_db
from api.dependencies.backend import authentication_backend
from api.dependencies.user_manager import get_user_manager
from api.dependencies.users import get_user_db
from database import db_helper
from database.models import User
from database.schemas.user import UserCreate

get_async_session_context = contextlib.asynccontextmanager(db_helper.get_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)
get_access_token_db_context = contextlib.asynccontextmanager(get_access_token_db)

if TYPE_CHECKING:
    from core.auth.user_manager import UserManager


def with_user_manager(func: Callable[..., Any]) -> Callable[..., Any]:
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    # Передаем user_manager в целевой метод
                    result = await func(user_manager=user_manager, *args, **kwargs)
                    return result

    return wrapper


class UserManagerHelper:
    @staticmethod
    @with_user_manager
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
    @with_user_manager
    async def get_user_by_email(
        user_manager: "UserManager",
        user_email: str,
    ) -> User:
        return await user_manager.get_by_email(user_email)

    @staticmethod
    @with_user_manager
    async def get_access_token(
        user_manager: "UserManager",
        credentials: OAuth2PasswordRequestForm,
    ) -> str | None:
        is_authenticated = await user_manager.authenticate(credentials)
        if (
            is_authenticated
            and is_authenticated.is_active
            and is_authenticated.is_verified
        ):
            user = await user_manager.get_by_email(credentials.username)
            async with get_async_session_context() as session:
                async with get_access_token_db_context(session) as token_db:
                    strategy = authentication_backend.get_strategy(token_db)
                    return await strategy.write_token(user)
        # user = await token_db.get_by_token(token)
        print("неверный логин или пароль или пользователь не активен/не подтвержден")
        return None

    @staticmethod
    @with_user_manager
    async def request_verify(
        user_manager: "UserManager",
        user: User,
    ) -> None:
        await user_manager.request_verify(user=user)

    @staticmethod
    @with_user_manager
    async def verify(
        user_manager: "UserManager",
        token: str,
    ) -> User:
        return await user_manager.verify(token=token)
