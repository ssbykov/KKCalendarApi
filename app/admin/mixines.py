from typing import Type, Any, Generic, cast

from sqladmin import action, ModelView
from starlette.requests import Request
from starlette.responses import RedirectResponse

from core.type_vars import T
from crud.mixines import GetBackNextIdMixin
from database import db_helper


class ActionNextBackMixin(Generic[T]):
    repo_type: Type[GetBackNextIdMixin[T]]
    model: Type[T]

    @action(name="back", label="< Назад", add_in_detail=True, add_in_list=False)
    async def back_record(self, request: Request) -> RedirectResponse:
        redirect_url = await self._get_redirect_url(request, is_next=False)
        return RedirectResponse(redirect_url, status_code=303)

    @action(name="next", label="Вперёд >", add_in_detail=True, add_in_list=False)
    async def next_record(self, request: Request) -> RedirectResponse:
        redirect_url = await self._get_redirect_url(request)
        return RedirectResponse(redirect_url, status_code=303)

    async def _get_redirect_url(self, request: Request, is_next: bool = True) -> str:
        referer = request.headers.get("referer", "")
        current_id = request.query_params.get("pks")
        if not current_id:
            return referer
        async for session in db_helper.get_session():
            repo = self.repo_type(session)
            model_view = cast(ModelView, self)
            list_query = model_view.list_query(request)
            if default_sort := self.get_sort_column(model_view.column_default_sort):
                sort_column = default_sort.key
                current_val = getattr(
                    await repo.get_by_id(int(current_id)), sort_column
                )
            else:
                sort_column = "id"
                current_val = int(current_id)

            url_id = await repo.get_adjacent_id(
                current_val=current_val,
                list_query=list_query,
                sort_column=sort_column,
                is_next=is_next,
            )

            if url_id:
                last_slash_index = referer.rfind("/")
                redirect_url = referer[: last_slash_index + 1] + str(url_id)
                return redirect_url
        return referer

    async def get_all(self, request: Request) -> list[Any] | None:
        async for session in db_helper.get_session():
            repo = self.repo_type(session)
            all_items = await repo.get_all()
            user = request.session.get("user")
            if hasattr(self.model, "user_id") and user and not user.get("is_superuser"):
                user_items = [
                    item for item in all_items if item.user_id == user.get("id")  # type: ignore
                ]
                return sorted(user_items, key=lambda item: item.id)
            return list(all_items)
        return None

    async def get_item_position(self, request: Request) -> dict[str, int | Any]:
        async for session in db_helper.get_session():
            print(
                await self.repo_type(session).get_async_position(
                    request.path_params["pk"],
                    column="id",
                )
            )
        all_items = await self.get_all(request)
        if all_items and hasattr(self, "page_size"):
            all_ids = sorted([item.id for item in all_items])
            index = all_ids.index(int(request.path_params["pk"]))
            list_page = len(all_ids[:index]) // self.page_size + 1
            return {"page": list_page, "item_position": index + 1}
        return {"page": 1, "item_position": 0}

    async def get_page_for_url(self, request: Request) -> str | None:
        item_position = await self.get_item_position(request)
        page = item_position.get("page")
        return f"?page={page}"

    @staticmethod
    def is_superuser(request: Request) -> bool:
        user = request.session.get("user")
        return isinstance(user, dict) and bool(user.get("is_superuser"))

    @staticmethod
    def get_sort_column(
        column_default_sort: Any,
    ) -> Any:
        if column_default_sort:
            if isinstance(column_default_sort, list):
                return column_default_sort[0][0]
            if isinstance(column_default_sort, tuple):
                return column_default_sort[0]
            else:
                return column_default_sort
        return None
