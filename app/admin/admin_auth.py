import contextlib

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication import JWTStrategy
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from api.dependencies.user_manager import get_user_manager
from api.dependencies.users import get_user_db
from core import config, settings
from database import db_helper

get_async_session_context = contextlib.asynccontextmanager(db_helper.get_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


class AdminAuth(AuthenticationBackend):
    async def login(
        self,
        request: Request,
    ) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        credentials = OAuth2PasswordRequestForm(
            username=username,
            password=password,
        )
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    if is_authenticated := await user_manager.authenticate(credentials):
                        if is_authenticated.is_active and is_authenticated.is_verified:
                            user = await user_manager.get_by_email(username)
                            jwt_strategy = JWTStrategy(
                                secret=settings.sql_admin.secret,
                                lifetime_seconds=config.settings.access_token.lifetime_seconds,
                            )
                            access_token = await jwt_strategy.write_token(user)
                            request.session.update({"token": access_token})
                        else:
                            print("негодный юзер")
                    else:
                        print("неверный логин или пароль")

        return True

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


sql_admin_authentication_backend = AdminAuth(secret_key=settings.sql_admin.secret)
