from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_users.exceptions import UserAlreadyExists

from actions.create_super_user import create_superuser
from core import settings
from database import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # await db_helper.init_db()
    try:
        await create_superuser(
            email=settings.super_user.email, password=settings.super_user.password
        )
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
