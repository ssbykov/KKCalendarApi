from sqlalchemy import select, not_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.crud.mixines import GetBackNextIdMixin
from app.database import Quote, SessionDep


def get_quote_repository(session: SessionDep) -> "QuoteRepository":
    return QuoteRepository(session)


class QuoteRepository(GetBackNextIdMixin[Quote]):
    session: AsyncSession
    model = Quote

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.session = session

    async def get_random_quote(
        self, excluded_ids: list[int] | None = None
    ) -> Quote | None:
        if excluded_ids is None:
            excluded_ids = []
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.lama),
            )
            .where(not_(self.model.id.in_(excluded_ids)))
            .order_by(func.random())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
