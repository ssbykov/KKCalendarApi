from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from admin.admin import init_admin
from admin.admin_auth import request_var
from api import router as api_router
from database import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # await db_helper.init_db()
    await init_admin(app)

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


@main_app.middleware("http")
async def reset_request_var(request: Request, call_next: Any) -> Any:
    try:
        response = await call_next(request)
        request_var.set(None)  # Сброс после запроса
        return response
    except Exception as e:
        request_var.set(None)  # Сброс при ошибке
        raise e
