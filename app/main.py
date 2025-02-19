from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_users.exceptions import UserAlreadyExists

from actions.create_superuser import create_superuser
from admin.admin import init_admin
from api import router as api_router
from core.config import settings
from database import db_helper
from utils.pars_class import CalendarDayPars


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # await db_helper.init_db()
    try:
        await create_superuser()
    except UserAlreadyExists as e:
        print("SuperUser already exists")
    # async for session in db_helper.get_session():
    #     parser = CalendarDayPars(session)
    #     await parser.get_days_info()
    yield
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)
main_app.include_router(router=api_router)
init_admin(main_app)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
