from contextvars import ContextVar

from fastapi.security import OAuth2PasswordRequestForm
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from api.dependencies.access_tokens_helper import access_tokens_helper
from api.dependencies.user_manager_helper import user_manager_helper
from core import settings
from database.schemas.user import UserCreate

request_var: ContextVar[dict] = ContextVar("user", default={})


class AdminAuth(AuthenticationBackend):

    async def login(
        self,
        request: Request,
    ) -> bool:
        form = await request.form()
        is_new_user = form.get("new_user")
        username, password = str(form["username"]), str(form["password"])

        if is_new_user:
            user_create = UserCreate(
                email=username,
                password=password,
                is_active=True,
                is_superuser=False,
                is_verified=False,
            )
            user = await user_manager_helper.create_user(user_create=user_create)
            await user_manager_helper.request_verify(user=user)
            return True
        else:
            credentials = OAuth2PasswordRequestForm(
                username=username,
                password=password,
            )

            access_token = await user_manager_helper.get_access_token(
                credentials=credentials
            )

            if access_token:
                request.session.update({"token": access_token})
                return True
        return False

    async def logout(self, request: Request) -> bool:
        # if token := request.session.get("token"):
        #     if access_token := await access_tokens_helper.get_access_token(token=token):
        #         await access_tokens_helper.delete_access_token(token=access_token)
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        is_valid = await access_tokens_helper.check_access_token(token=token)
        if not is_valid:
            await self.logout(request)
            return False

        access_token = await access_tokens_helper.get_access_token(token=token)
        if not access_token:
            return False

        user_data = await user_manager_helper.get_user_by_id(
            user_id=access_token.user_id
        )
        if not user_data:
            return False
        request_var.set(
            {
                "email": user_data.email,
                "id": user_data.id,
                "is_active": user_data.is_active,
                "is_superuser": user_data.is_superuser,
                "is_verified": user_data.is_verified,
            },
        )

        return True


sql_admin_authentication_backend = AdminAuth(secret_key=settings.sql_admin.secret)
