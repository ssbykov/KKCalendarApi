from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.staticfiles import StaticFiles

from admin.init_admin import init_admin
from api import router as api_router
from core.logger_init import init_logger
from database import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await db_helper.synch_backups()
    await init_admin(app)
    yield
    await db_helper.dispose()


def init_main_app() -> FastAPI:
    main_app = FastAPI(
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )
    init_logger()
    main_app.mount("/static", StaticFiles(directory="./static"), name="static")

    main_app.include_router(router=api_router)

    return main_app
