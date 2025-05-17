import io

import pandas as pd
from fastapi import HTTPException
from sqladmin import ModelView, action, expose, BaseView
from sqladmin.templating import _TemplateResponse
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse

from admin.mixines import CustomNavMixin
from admin.utils import check_superuser
from crud.lamas import LamaRepository
from crud.quotes import QuoteRepository
from database import Quote, db_helper
from database.schemas.lama import LamaSchemaCreate
from database.schemas.quote import QuoteSchemaCreate


class QuoteAdmin(
    ModelView,
    CustomNavMixin[Quote],
    model=Quote,
):
    repo_type = QuoteRepository
    name_plural = "Цитаты"
    name = "Цитата"
    icon = "fa-solid fa-quote-left"

    column_list = ["lama", "text"]
    column_details_exclude_list = ("id", "lama_id")
    column_labels = {
        "text": "Цитата",
        "lama": "Автор",
    }
    can_edit = True
    can_delete = True
    can_export = False

    def is_visible(self, request: Request) -> bool:
        return check_superuser(request)

    def is_accessible(self, request: Request) -> bool:
        return check_superuser(request)

    @action(
        name="import_excel",
        label="Импорт из Excel",
        add_in_detail=True,
        add_in_list=True,
    )
    async def import_excel_action(self, request: Request) -> _TemplateResponse:
        context = {
            "model_admin": self,
            "request": request,
        }

        return await self.templates.TemplateResponse(
            request, name="import_excel.html", context=context
        )


class QuoteView(BaseView):

    def is_visible(self, request: Request) -> bool:
        return False

    @expose("/import-quotes", methods=["POST"], include_in_schema=False)
    async def process_import(self, request: Request) -> RedirectResponse:
        """Обработка POST-запроса с файлом"""
        form = await request.form()
        file = form["file"]

        try:
            count: int = 0

            if not file:
                raise HTTPException(status_code=400, detail="Файл не загружен")

            if not isinstance(file, UploadFile):
                raise HTTPException(status_code=400, detail="Некорректный формат файла")

            if not file.filename or not isinstance(file.filename, str):
                raise HTTPException(status_code=400, detail="Имя файла отсутствует")

            if not file.filename.endswith((".xlsx", ".xls")):
                raise ValueError("Требуется файл Excel (.xlsx или .xls)")

            contents = await file.read()
            df = pd.read_excel(io.BytesIO(contents))

            async for session in db_helper.get_session():
                lama_repo = LamaRepository(session)

                for _, row in df.iterrows():
                    if pd.isna(author := row.Author):
                        continue
                    quote = row.Quote
                    lama = await lama_repo.get_lama_by_name(author)
                    if lama:
                        lama_id = lama.id
                    else:
                        lama_obj = LamaSchemaCreate(name=author)
                        lama_id = await lama_repo.add_lama(lama_obj)

                    quote_obj = QuoteSchemaCreate(lama_id=lama_id, text=quote)
                    orm_quote = quote_obj.to_orm()
                    session.add(orm_quote)
                    count += 1
                await session.commit()

            response = RedirectResponse(
                url=request.url_for("admin:list", identity="quote"), status_code=303
            )

            response.set_cookie(
                "flash", f"Loaded: {count} quotes", max_age=1, httponly=True
            )
            return response
        except Exception as e:
            request.session["error"] = str(e)
            return RedirectResponse(
                url="/admin/quote/action/import-excel", status_code=303
            )
