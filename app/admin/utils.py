from typing import Callable, Type, Any, Union

from markupsafe import Markup
from sqlalchemy import Text
from sqlalchemy.orm import InstrumentedAttribute
from starlette.requests import Request

from database import BaseWithId


def check_superuser(request: Request) -> bool:
    return bool(request.session.get("user", {}).get("is_superuser"))


def text_formater(
    model: Type[BaseWithId],
) -> dict[str | InstrumentedAttribute[Any], Callable[[Any, Any], Any]]:
    formater = lambda m, f: Markup(
        f"<div style='white-space: pre-wrap; max-width: 800px;'>{getattr(m, f)}</div>"
    )
    columns = list(model.__table__.columns)
    return {
        column.name: formater for column in columns if isinstance(column.type, Text)
    }
