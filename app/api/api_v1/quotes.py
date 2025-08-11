from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core import settings
from app.database import Quote
from app.database.crud.quotes import QuoteRepository, get_quote_repository
from app.database.schemas.quote import QuoteSchema

router = APIRouter(
    tags=["Quotes"],
    prefix=settings.api.v1.quotes,
)
router.include_router(
    router,
)


class ExcludedIdsRequest(BaseModel):
    excluded_ids: list[int]


@router.post("/", response_model=QuoteSchema)
async def get_random_quote(
    body: ExcludedIdsRequest,
    repo: Annotated[QuoteRepository, Depends(get_quote_repository)],
) -> Quote | str:
    try:
        quote = await repo.get_random_quote(body.excluded_ids)
        return quote or "Нет цитат"
    except Exception as e:
        return f"Произошла ошибка: {e}"


@router.get("/count", response_model=int)
async def get_quotes_count(
    repo: Annotated[QuoteRepository, Depends(get_quote_repository)],
) -> int:
    try:
        count = await repo.get_count_items()
        return count
    except Exception as e:
        return 0
