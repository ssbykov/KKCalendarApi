from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser
from app.database.crud.users import UsersRepository
from app.database.models import User


class UserAdmin(
    CustomModelView[User],
    model=User,
):
    repo_type = UsersRepository
    name_plural = "Пользователи"
    name = "Пользователь"
    icon = "fa-solid fa-user"

    column_list = ["id", "email", "is_verified"]
    can_edit = False
    can_delete = False
    can_export = False
    can_create = False
    can_view_details = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
