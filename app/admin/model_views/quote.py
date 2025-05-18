import io
from difflib import SequenceMatcher

import pandas as pd
from fastapi import HTTPException
from sqladmin import ModelView, action, expose, BaseView
from sqladmin.templating import _TemplateResponse
from sqlalchemy import select
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse

from admin.mixines import CustomNavMixin
from admin.utils import check_superuser
from crud.lamas import LamaRepository
from crud.quotes import QuoteRepository
from database import Quote, db_helper, Lama
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
        add_in_detail=False,
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

    MAX_RATIO = 0.75

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

            # Удаляем строки с пустыми авторами
            df = df.dropna(subset=["Author"])

            async for session in db_helper.get_session():
                lama_repo = LamaRepository(session)

                # Получаем все существующие цитаты один раз
                result = await session.execute(select(Quote.text))
                quotes_in_base = result.scalars().all()

                # Получаем все Лам из базы за один раз
                result = await session.execute(select(Lama))
                lamas_in_base = result.scalars().all()

                # Создаем словарь для быстрого поиска авторов
                existing_lamas = {lama.name: lama.id for lama in lamas_in_base}

                # Предварительная фильтрация дубликатов
                def is_unique(quote, max_ratio=self.MAX_RATIO):
                    return not any(
                        SequenceMatcher(None, q, quote).ratio() > max_ratio
                        for q in quotes_in_base
                    )

                # Применяем фильтрацию ко всему DataFrame
                unique_quotes = df[df["Quote"].apply(is_unique)]

                # Группируем по авторам для эффективной вставки
                grouped = unique_quotes.groupby("Author")

                count = 0
                for author, group in grouped:
                    if author not in existing_lamas:
                        lama_obj = LamaSchemaCreate(name=author)
                        existing_lamas[author] = await lama_repo.add_lama(lama_obj)

                    for _, row in group.iterrows():
                        quote_obj = QuoteSchemaCreate(
                            lama_id=existing_lamas[author], text=row["Quote"]
                        )
                        session.add(quote_obj.to_orm())
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
