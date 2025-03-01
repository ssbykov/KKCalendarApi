from contextvars import ContextVar

super_user_id: ContextVar[int | None] = ContextVar("super_user_id", default=None)
