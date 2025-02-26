import logging
import re
from typing import Optional, TYPE_CHECKING, Union

from fastapi_users import BaseUserManager, IntegerIDMixin, InvalidPasswordException

from core import settings, config
from database.models import User
from database.schemas.user import UserCreate
from utils.email_sender import send_verification_email

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from fastapi import Request


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_register(
        self,
        user: User,
        request: Optional["Request"] = None,
    ) -> None:
        logger.warning("User %r has registered.", user.id)

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ) -> None:
        logger.warning(
            "User %r has forgot their password. Reset token: %r", user.id, token
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ) -> None:
        verification_url = (
            f"http://{config.settings.run.host}"
            f":{config.settings.run.port}"
            f"/{config.settings.api.auth_url}"
            f"/verify/?token={token}"
        )
        await send_verification_email(
            user_email=user.email,
            url_verification=verification_url,
            token=token,
            action="verification",
        )
        logger.warning(
            "Verification requested for user %r. Verification token: %r", user.id, token
        )

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:

        if len(password) < 4:
            raise InvalidPasswordException(
                reason="Пароль должен быть не менее 8 символов"
            )
        if not re.search(r"\d", password):
            raise InvalidPasswordException(reason="Пароль должен содержать цифры")

        if not re.search(r"[A-Z]", password):
            raise InvalidPasswordException(
                reason="Пароль должен содержать заглавные буквы"
            )

        if not re.search(r"[a-z]", password):
            raise InvalidPasswordException(
                reason="Пароль должен содержать строчные буквы"
            )

        if user.email in password:
            raise InvalidPasswordException(reason="Пароль не должен содержать e-mail")
