from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from admin.init_admin import init_admin
from api import router as api_router
from database import db_helper
from utils.html_parser import HtmlParser


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # await db_helper.init_db()
    await init_admin(app)

    # async for session in db_helper.get_session():
    #     parser = HtmlParser(session)
    #     await parser.get_days_info()
    yield
    await db_helper.dispose()


def init_main_app() -> FastAPI:
    main_app = FastAPI(
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )

    main_app.include_router(router=api_router)

    return main_app
