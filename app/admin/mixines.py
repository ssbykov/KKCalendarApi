from typing import Type

from sqladmin import action
from starlette.requests import Request
from starlette.responses import RedirectResponse

from crud.mixines import GetBackNextIdMixin
from database import db_helper


class ActionNextBackMixin:
    repo_type: Type[GetBackNextIdMixin]

    @action(name="back", label="< Back", add_in_detail=True)
    async def back_record(self, request: Request) -> RedirectResponse:
        redirect_url = await self._get_redirect_url(request, is_next=False)
        return RedirectResponse(redirect_url, status_code=303)

    @action(name="next", label="Next >", add_in_detail=True)
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
