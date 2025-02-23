import uvicorn

from admin.admin import init_admin
from api import router as api_router
from core.config import settings
from main_app import main_app

main_app.include_router(router=api_router)
init_admin(main_app)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
