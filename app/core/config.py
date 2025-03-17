from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class SqlAdmin(BaseModel):
    templates: str
    jwt_secret: str
    secret: str


class ImageStorage(BaseModel):
    root: str = str(Path(__file__).resolve().parent.parent)
    storage: str = "/static/images"


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
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
    def auth_url(self) -> str:
        parts = (self.prefix[1:], self.v1.prefix, self.v1.auth)
        return "".join(parts)

    @property
    def token_url(self) -> str:
        return self.auth_url + "/login"


class EmailSettings(BaseModel):
    host: str
    port: int
    username: str
    password: str
    admin_email: str
    templates_dir: str


class CalendarSettings(BaseModel):
    secret_file: str
    calendar_id: str


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
    image_storage: ImageStorage = ImageStorage()
    sql_admin: SqlAdmin
    access_token: AccessToken
    db: DbSettings
    super_user: SuperUser
    email: EmailSettings
    calendar: CalendarSettings


# noinspection PyArgumentList
settings = Settings()  # type: ignore[call-arg]
