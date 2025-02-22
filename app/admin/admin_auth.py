from fastapi.security import OAuth2PasswordRequestForm
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from api.dependencies.user_manager_helper import user_manager_helper
from core import settings
from core.auth.user_manager_helper import UserManagerHelper
from database.schemas.user import UserCreate


class AdminAuth(AuthenticationBackend):
    def __init__(
        self,
        user_manager: UserManagerHelper,
        secret_key: str = settings.sql_admin.secret,
    ):
        super().__init__(secret_key=secret_key)
        self.user_manager_helper = user_manager

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
            user = await self.user_manager_helper.create_user(user_create=user_create)
            await self.user_manager_helper.request_verify(user=user)

        else:
            credentials = OAuth2PasswordRequestForm(
                username=username,
                password=password,
            )

            access_token = await self.user_manager_helper.get_access_token(
                credentials=credentials
            )

            if access_token:
                request.session.update({"token": access_token})
                return True
        return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True


sql_admin_authentication_backend = AdminAuth(user_manager=user_manager_helper)
