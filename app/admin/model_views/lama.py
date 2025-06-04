from markupsafe import Markup
from starlette.requests import Request

from app.admin.custom_model_view import CustomModelView
from app.admin.model_views.event_photo import photo_url
from app.admin.utils import check_superuser
from app.database.crud.lamas import LamaRepository
from app.database import db_helper, Lama


class LamaAdmin(
    CustomModelView[Lama],
    model=Lama,
):
    repo_type = LamaRepository
    name_plural = "Учителя"
    name = "Лама"
    icon = "fa-solid fa-person"

    column_list = ("name",)
    column_searchable_list = ("name",)
    column_details_exclude_list = (
        "id",
        "photo_id",
        "lama",
    )
    form_excluded_columns = ("lama",)
    column_labels = {
        "name": "Имя",
        "description": "Описание",
        "photo": "Фотография",
    }
    can_edit = True
    can_delete = True
    can_export = False

    column_formatters_detail = {
        Lama.photo: lambda model, _: (
            Markup(photo_url(model.photo.photo_data))
            if hasattr(model, "photo") and model.photo
            else ""
        ),
    }

    async def check_restrictions_create(
        self, form_data_dict: dict[str, str], request: Request | None = None
    ) -> str | None:
        pk = getattr(request, "path_params", {}).get("pk") if request else None
        name = form_data_dict.get("name", "").strip()

        lama = await self.get_lama_by_name(name)
        if lama:
            if pk is None or lama.id != int(pk):
                return "Данное название уже используется"

        photo_id = form_data_dict.get("photo")
        if photo_id is None:
            return None

        lama = await self.get_lama_by_photo(int(photo_id))
        if lama:
            if pk is None or lama.id != int(pk):
                return "Данное фото уже используется"

        return None

    async def get_lama_by_name(self, name: str) -> Lama | None:
        async for session in db_helper.get_session():
            repo = self.repo_type(session)
            return await repo.get_lama_by_name(name)
        return None

    async def get_lama_by_photo(self, photo_id: int) -> Lama | None:
        async for session in db_helper.get_session():
            repo = self.repo_type(session)
            return await repo.get_lama_by_photo(photo_id)
        return None

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)
