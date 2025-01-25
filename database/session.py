from typing import Annotated, AsyncGenerator, Type, Any

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.config import settings
from database.database import Base
from models.day_info import YelamModel, HaircuttingModel, LaModel, ElementModel, ArchModel, DayInfo
from schemas.day_info import DayDataSchema, ArchSchema, ElementSchema, HaircuttingSchema, LaSchema, YelamSchema

engine = create_async_engine(settings.DATABASE_URL, future=True, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]

init_data: list[dict[str, Any]] = [
    {"model_class": YelamModel, "schema_class": YelamSchema},
    {"model_class": HaircuttingModel, "schema_class": HaircuttingSchema},
    {"model_class": LaModel, "schema_class": LaSchema},
    {"model_class": ElementModel, "schema_class": ElementSchema},
    {"model_class": ArchModel, "schema_class": ArchSchema},
]

days = [
    {
        "date": "23.01.2025",
        "moon_day": "24.12i",
        "first_element_id": 1,
        "second_element_id": 2,
        "arch_id": 3,
        "la_id": 3,
        "yelam_id": 2,
        "haircutting_id": 5,
        "descriptions": []
    },
    {
        "date": "24.01.2025",
        "moon_day": "25.12i",
        "first_element_id": 2,
        "second_element_id": 3,
        "arch_id": 4,
        "la_id": 5,
        "yelam_id": 3,
        "haircutting_id": 4,
        "descriptions": []
    }
]


async def init_model(session: AsyncSession, model_class: Type[Base], schema_class: Type[DayDataSchema]) -> None:
    # async for session in get_session():
    result = await session.execute(select(func.count()).select_from(model_class))
    count = result.scalar()
    if count == 0:
        for el in model_class.init_data:
            el_schema = schema_class(**el)
            session.add(el_schema.to_orm(model_class))
        # await session.commit()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async for session in get_session():
        for data in init_data:
            await init_model(session, **data)

        for day in days:
            session.add(DayInfo(**day))
        await session.commit()
