from contextvars import ContextVar
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from database.schemas.user import UserRead

request_var: ContextVar[Optional["UserRead"]] = ContextVar("user", default=None)
super_user_id: ContextVar[int | None] = ContextVar("super_user_id", default=None)
