from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_users.exceptions import UserAlreadyExists

from api.dependencies.user_manager_helper import user_manager_helper
from database import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # await db_helper.init_db()
    try:
        await user_manager_helper.create_superuser()
    except UserAlreadyExists:
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
