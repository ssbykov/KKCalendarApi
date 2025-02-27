from contextvars import ContextVar

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserAlreadyExists
from pydantic import ValidationError, EmailStr
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from api.dependencies.access_tokens_helper import access_tokens_helper
from core import settings
from core.auth.user_manager_helper import UserManagerHelper
from database.schemas.admin_auth_response import AdminAuthResponse
from database.schemas.user import UserCreate, UserRead

request_var: ContextVar[UserRead | None] = ContextVar("user", default=None)


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str = settings.sql_admin.secret) -> None:
        super().__init__(secret_key=secret_key)
        self.user_manager_helper = UserManagerHelper()

    async def login_with_info(
        self,
        request: Request,
    ) -> AdminAuthResponse:
        form = await request.form()
        is_new_user = form.get("new_user")
        username, password = str(form["username"]), str(form["password"])

        if is_new_user:
            try:
                user_create = UserCreate(
                    email=username,
                    password=password,
                    is_active=True,
                    is_superuser=False,
                    is_verified=False,
                )
            except ValidationError:
                return AdminAuthResponse(
                    is_ok=False,
                    error="Проверьте правильность email",
                )
            if await self.user_manager_helper.get_user_by_email(user_email=username):
                return AdminAuthResponse(
                    is_ok=False,
                    error="Пользователь с таким email уже существует",
                )
            try:
                user = await self.user_manager_helper.create_user(
                    user_create=user_create
                )
                await self.user_manager_helper.request_verify(user=user)
                return AdminAuthResponse(
                    is_ok=False,
                    message="Пользователь успешно зарегистрирован. "
                    "Дождитесь Уведомление о верификации на почту.",
                )
            except InvalidPasswordException as e:
                return AdminAuthResponse(
                    is_ok=False,
                    error=e.reason,
                )
            except Exception as e:
                return AdminAuthResponse(
                    is_ok=False,
                    error=str(e),
                )

        else:
            credentials = OAuth2PasswordRequestForm(
                username=username,
                password=password,
            )

            if not (
                user := await self.user_manager_helper.get_user(credentials=credentials)
            ):
                return AdminAuthResponse(
                    is_ok=False,
                    error="неверный логин/пароль или пользователь не подтвержден.,",
                )

            if access_token := await access_tokens_helper.write_token(user=user):
                request.session.update({"token": access_token})
                return AdminAuthResponse(is_ok=True)
        return AdminAuthResponse(
            is_ok=False,
            error="Неизвестная ошибка",
        )

    async def logout(self, request: Request) -> bool:
        if token := request.session.get("token"):
            access_token = await access_tokens_helper.get_access_token(token=token)
            user_data = await self.user_manager_helper.get_user_by_id(
                user_id=access_token.user_id
            )
            await access_tokens_helper.destroy_token(token=token, user=user_data)
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        if not await access_tokens_helper.check_access_token(token=token):
            await self.logout(request)
            return False

        if not (
            access_token := await access_tokens_helper.get_access_token(token=token)
        ):
            return False

        if user_data := await self.user_manager_helper.get_user_by_id(
            user_id=access_token.user_id
        ):
            user_read = UserRead(
                email=user_data.email,
                id=user_data.id,
                is_active=user_data.is_active,
                is_superuser=user_data.is_superuser,
                is_verified=user_data.is_verified,
            )
            request_var.set(user_read)
            return True
        return False

    async def create_superuser(
        self,
        email: EmailStr = settings.super_user.email,
        password: str = settings.super_user.password,
        is_active: bool = True,
        is_superuser: bool = True,
        is_verified: bool = True,
    ) -> None:
        user_create = UserCreate(
            email=email,
            password=password,
            is_active=is_active,
            is_superuser=is_superuser,
            is_verified=is_verified,
        )
        try:
            await self.user_manager_helper.create_user(user_create=user_create)
        except UserAlreadyExists:
            print("SuperUser already exists")


# sql_admin_authentication_backend = AdminAuth(secret_key=settings.sql_admin.secret)
