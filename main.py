from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from database.session import get_session, init_db
from repositories.pars_class import CalendarDayPars
from routers import day_info_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    async for session in get_session():
        parser = CalendarDayPars(session)
        await parser.get_days_info()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(day_info_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
