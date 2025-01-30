import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = (
        f"postgresql+asyncpg://"
        f"{os.getenv('DB_USER')}"
        f":{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}"
        f":{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_BASE')}"
    )


settings = Settings()
