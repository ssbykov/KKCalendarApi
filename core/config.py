import os

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class SqlAdminSettings(BaseModel):
    templates_dir: str = "admin/templates/"


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DbSettings(BaseModel):
    url: PostgresDsn = (
        f"postgresql+asyncpg://"
        f"{os.getenv('DB_USER')}"
        f":{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}"
        f":{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_BASE')}"
    )
    echo: bool = False


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api_v1_prefix: str = "/api/v1"
    db: DbSettings = DbSettings()
    sql_admin: SqlAdminSettings = SqlAdminSettings()


settings = Settings()
