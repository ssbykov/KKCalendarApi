from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from database.session import init_db
from routers import day_info_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(day_info_router)
# @app.get("/")
# async def read_root():
#     return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
