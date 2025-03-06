from typing import Type, Any, Generic

from sqladmin import action
from starlette.requests import Request
from starlette.responses import RedirectResponse

from core.type_vars import T
from crud.mixines import GetBackNextIdMixin, CommonMixin
from database import db_helper


class ActionNextBackMixin(Generic[T]):
    repo_type: Type[GetBackNextIdMixin[T]]

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
            if is_next:
                url_id = await repo.get_next_id(int(current_id))
            else:
                url_id = await repo.get_back_id(int(current_id))

            if url_id:
                last_slash_index = referer.rfind("/")
                redirect_url = referer[: last_slash_index + 1] + str(url_id)
                return redirect_url
        return referer


class CommonActionsMixin(Generic[T]):
    repo_type: Type[CommonMixin[T]]
    model: Type[T]

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

    async def get_page_for_url(self, request: Request) -> str | None:
        all_items = await self.get_all(request)
        if all_items and hasattr(self, "page_size"):
            all_ids = sorted([item.id for item in all_items])
            index = all_ids.index(int(request.path_params["pk"]))
            list_page = len(all_ids[:index]) // self.page_size + 1
            return f"?page={list_page}"
        return None
