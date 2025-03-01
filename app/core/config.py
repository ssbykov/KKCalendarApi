from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class SqlAdminSettings(BaseModel):
    templates_dir: str = "app/admin/templates/"


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class SuperUser(BaseModel):
    email: str
    password: str


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    days: str = "/days"
    auth: str = "/auth"
    users: str = "/users"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def token_url(self) -> str:
        parts = (self.prefix[1:], self.v1.prefix, self.v1.auth, "/login")
        return "".join(parts)


class DbSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: int
    database: str

    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn(
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        )

    echo: bool = False
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
    access_token: Optional[AccessToken] = None
    db: Optional[DbSettings] = None
    super_user: Optional[SuperUser] = None


settings = Settings()
