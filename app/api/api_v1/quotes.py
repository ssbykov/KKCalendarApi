from typing import Sequence, Annotated

from fastapi import APIRouter, Depends

from core import settings
from database.crud.quotes import QuoteRepository, get_quote_repository
from database import Quote
from database.schemas.quote import QuoteSchema

router = APIRouter(
    tags=["Quotes"],
)
router.include_router(
    router,
    prefix=settings.api.v1.quotes,
)


@router.get("/quote", response_model=QuoteSchema)
async def get_random_quote(
    repo: Annotated[QuoteRepository, Depends(get_quote_repository)],
) -> Sequence[Quote] | str:
    try:
        quote = await repo.get_random_quote()
        return quote
    except Exception as e:
        return f"Произошла ошибка: {e}"
