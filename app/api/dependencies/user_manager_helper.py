from core import settings
from core.auth.user_manager_helper import UserManagerHelper

user_manager_helper = UserManagerHelper(
    default_email=settings.super_user.email,
    default_password=settings.super_user.email,
)
