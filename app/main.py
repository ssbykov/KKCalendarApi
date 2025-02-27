import uvicorn

from core.config import settings
from main_app import init_main_app

main_app = init_main_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
