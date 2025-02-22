import logging
from typing import Optional, TYPE_CHECKING

from fastapi_users import BaseUserManager, IntegerIDMixin

from core import settings, config
from database.models import User
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
