from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from api_v1 import router as api_v1_router
from core.config import settings
from database import db_helper
from repositories.pars_class import CalendarDayPars


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # await db_helper.init_db()
    # async for session in db_helper.get_session():
    #     parser = CalendarDayPars(session)
    #     await parser.get_days_info()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=api_v1_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
