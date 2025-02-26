from contextvars import ContextVar

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.exceptions import UserNotExists
from pydantic import ValidationError
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from api.dependencies.access_tokens_helper import access_tokens_helper
from api.dependencies.user_manager_helper import user_manager_helper
from core import settings
from database.schemas.admin_auth_response import AdminAuthResponse
from database.schemas.user import UserCreate, UserRead

request_var: ContextVar[UserRead | None] = ContextVar("user", default=None)


class AdminAuth(AuthenticationBackend):

    @staticmethod
    async def login_with_info(
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
            except ValidationError as e:
                return AdminAuthResponse(
                    is_ok=False,
                    error=str(e),
                )
            try:
                if await user_manager_helper.get_user_by_email(user_email=username):
                    return AdminAuthResponse(
                        is_ok=False,
                        error="Пользователь с таким email уже существует",
                    )
            except UserNotExists:
                user = await user_manager_helper.create_user(user_create=user_create)
                await user_manager_helper.request_verify(user=user)
                return AdminAuthResponse(
                    is_ok=False,
                    message="Пользователь успешно зарегистрирован. "
                    "Дождитесь Уведомление о верификации на почту.",
                )
            return AdminAuthResponse(
                is_ok=False,
                error="Неизвестная ошибка",
            )

        else:
            credentials = OAuth2PasswordRequestForm(
                username=username,
                password=password,
            )

            if not (
                user := await user_manager_helper.get_user(credentials=credentials)
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
            user_data = await user_manager_helper.get_user_by_id(
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

        if user_data := await user_manager_helper.get_user_by_id(
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


sql_admin_authentication_backend = AdminAuth(secret_key=settings.sql_admin.secret)
