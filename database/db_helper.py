from typing import Annotated, AsyncGenerator, Type, Any

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.config import settings
from models import *
from models.base import Base
from schemas.day_info import (
    DayDataSchema,
    ArchSchema,
    ElementSchema,
    HaircuttingSchema,
    LaSchema,
    YelamSchema,
)


class DbHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.async_session = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session() as session:
            yield session

    @staticmethod
    async def _init_model(
        session: AsyncSession,
        model_class: Type[Base],
        schema_class: Type[DayDataSchema],
    ) -> None:
        result = await session.execute(select(func.count()).select_from(model_class))
        count = result.scalar()
        if count == 0:
            for el in model_class.init_data:
                el_schema = schema_class(**el)
                session.add(el_schema.to_orm())

    async def init_db(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async for session in self.get_session():
            for data in init_data:
                await self._init_model(session, **data)
            await session.flush()
            await session.commit()


db_helper = DbHelper(url=settings.DB_URL, echo=settings.DB_ECHO)
SessionDep = Annotated[AsyncSession, Depends(db_helper.get_session)]

init_data: list[dict[str, Any]] = [
    {"model_class": YelamModel, "schema_class": YelamSchema},
    {"model_class": HaircuttingModel, "schema_class": HaircuttingSchema},
    {"model_class": LaModel, "schema_class": LaSchema},
    {"model_class": ElementModel, "schema_class": ElementSchema},
    {"model_class": ArchModel, "schema_class": ArchSchema},
]
