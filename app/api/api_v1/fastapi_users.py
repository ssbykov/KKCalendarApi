from fastapi_users import FastAPIUsers

from api.dependencies.backend import authentication_backend
from api.dependencies.user_manager import get_user_manager
from database.models import User

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [authentication_backend],
)
