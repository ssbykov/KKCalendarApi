import contextlib
from datetime import datetime, timedelta, timezone
from typing import Callable, Any

from api.dependencies.access_tokens import get_access_token_db
from core import settings
from database import db_helper

get_async_session_context = contextlib.asynccontextmanager(db_helper.get_session)
get_access_token_db_context = contextlib.asynccontextmanager(get_access_token_db)


def with_token_db(func: Callable[..., Any]) -> Callable[..., Any]:
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with get_async_session_context() as session:
            async with get_access_token_db_context(session) as token_db:
                result = await func(token_db=token_db, *args, **kwargs)
                return result

    return wrapper


class AccessTokensHelper:
    async def check_access_token(
        self,
        token: str,
    ) -> bool:
        token = await self.get_access_token(token=token)
        if token.created_at + timedelta(
            seconds=settings.access_token.lifetime_seconds
        ) > datetime.now(tz=timezone.utc):
            return True
        return False

    @staticmethod
    @with_token_db
    async def get_access_token(
        token: str,
        token_db: Any,
    ) -> str | None:
        return await token_db.get_by_token(token=token)
