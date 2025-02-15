import os

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class SqlAdminSettings(BaseModel):
    templates_dir: str = "app/admin/templates/"


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    days: str = "/days"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DbSettings(BaseModel):
    url: PostgresDsn = (
        f"postgresql+asyncpg://"
        f"{os.getenv('DB_USER')}"
        f":{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}"
        f":{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_BASE')}"
    )
    echo: bool = True
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    sql_admin: SqlAdminSettings = SqlAdminSettings()
    db: DbSettings = DbSettings()


settings = Settings()
