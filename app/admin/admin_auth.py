import functools
import inspect
from typing import Callable, Any

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserAlreadyExists
from pydantic import ValidationError, EmailStr
from sqladmin.authentication import AuthenticationBackend
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from core import settings
from core.auth.access_tokens_helper import AccessTokensHelper
from core.auth.user_manager_helper import UserManagerHelper
from core.context_vars import super_user_id
from database.schemas.admin_auth_response import AdminAuthResponse
from database.schemas.user import UserCreate, UserRead


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str = settings.sql_admin.secret) -> None:
        super().__init__(secret_key=secret_key)
        self.user_manager_helper = UserManagerHelper()
        self.access_tokens_helper = AccessTokensHelper()

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

            if access_token := await self.access_tokens_helper.write_token(user=user):
                request.session.update({"token": access_token})
                request.session.update({"user": user.model_dump()})
                return AdminAuthResponse(is_ok=True)
        return AdminAuthResponse(
            is_ok=False,
            error="Неизвестная ошибка",
        )

    async def logout(self, request: Request) -> bool:
        if token := request.session.get("token"):
            if access_token := await self.access_tokens_helper.get_access_token(
                token=token
            ):
                user_data = await self.user_manager_helper.get_user_by_id(
                    user_id=access_token.user_id
                )
                await self.access_tokens_helper.destroy_token(
                    token=token, user=user_data
                )
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        if not await self.access_tokens_helper.check_access_token(token=token):
            await self.logout(request)
            return False

        if not (
            access_token := await self.access_tokens_helper.get_access_token(
                token=token
            )
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
            super_user = await self.user_manager_helper.create_user(
                user_create=user_create
            )
        except UserAlreadyExists:
            super_user = await self.user_manager_helper.get_user_by_email(
                user_email=email
            )
        super_user_id.set(super_user.id)


def owner_required(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    async def wrapper_decorator(*args: Any, **kwargs: Any) -> Any:
        view, request = args[0], args[1]
        is_owner = await check_owner(view=view, request=request)
        if not is_owner and not request.session.get("user").get("is_superuser"):
            raise HTTPException(status_code=404)

        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper_decorator


async def check_owner(view: Any, request: Request) -> bool:
    identity = request.path_params.get("identity")
    if not (object_id := request.path_params.get("pk")):
        object_id = request.query_params.get("pks")
    model_view = [v for v in view.views if v.identity == identity][0]
    obj = await model_view.get_object_for_details(object_id)
    user = request.session.get("user", {})
    if hasattr(obj, "user_id"):
        return bool(obj.user_id == user.get("id"))
    return False
