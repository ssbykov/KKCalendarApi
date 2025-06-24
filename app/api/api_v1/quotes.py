from typing import Sequence, Annotated

from fastapi import APIRouter, Depends

from app.core import settings
from app.database.crud.quotes import QuoteRepository, get_quote_repository
from app.database import Quote
from app.database.schemas.quote import QuoteSchema

router = APIRouter(
    tags=["Quotes"],
)
router.include_router(
    router,
    prefix=settings.api.v1.quotes,
)


@router.post("/quote", response_model=QuoteSchema)
async def get_random_quote(
    excluded_ids: list[int],
    repo: Annotated[QuoteRepository, Depends(get_quote_repository)],
) -> Quote | str:
    try:
        quote = await repo.get_random_quote(excluded_ids)
        return quote or "Нет цитат"
    except Exception as e:
        return f"Произошла ошибка: {e}"
