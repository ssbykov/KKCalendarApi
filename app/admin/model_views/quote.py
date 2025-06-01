from fastapi import HTTPException
from sqladmin import action, expose, BaseView
from sqladmin.templating import _TemplateResponse
from sqlalchemy import select
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser, text_formater
from app.celery_worker import redis_client, check_job_status
from app.database import Quote, db_helper
from app.database.crud.quotes import QuoteRepository
from app.tasks.quoters import is_quote_unique, run_process_import, TASK_NAME


class QuoteAdmin(
    CustomModelView[Quote],
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

    column_formatters_detail = text_formater(Quote)
    column_formatters = text_formater(Quote)

    column_searchable_list = ["text"]

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
        return await get_template(self, request)

    async def check_restrictions_create(
        self, form_data_dict: dict[str, str], request: Request | None = None
    ) -> str | None:
        pk = getattr(request, "path_params", {}).get("pk") if request else -1
        quote = form_data_dict.get("text", "").strip()
        async for session in db_helper.get_session():
            result = await session.execute(
                select(Quote.text).where(Quote.id != int(pk))
            )
            quotes_in_base = result.scalars().all()
            if not is_quote_unique(
                quote=quote,
                existing=quotes_in_base,
                new_quotes=set(),
            ):
                return "В базе есть цитата в совпадением более 75%"
        return None


class QuoteView(BaseView):

    def is_visible(self, request: Request) -> bool:
        return False

    @expose("/import-quotes", methods=["POST", "GET"], include_in_schema=False)
    async def process_import(
        self, request: Request
    ) -> RedirectResponse | _TemplateResponse:

        if request.method == "GET":
            return await get_template(self, request)

        form = await request.form()
        file = form["file"]

        if not file:
            raise HTTPException(status_code=400, detail="Файл не загружен")

        if not isinstance(file, UploadFile):
            raise HTTPException(status_code=400, detail="Некорректный формат файла")

        if not file.filename or not isinstance(file.filename, str):
            raise HTTPException(status_code=400, detail="Имя файла отсутствует")

        if not file.filename.endswith((".xlsx", ".xls")):
            raise ValueError("Требуется файл Excel (.xlsx или .xls)")

        contents = await file.read()

        task_import = check_job_status(TASK_NAME)
        if task_import and task_import.status == "SUCCESS" or not task_import:
            task_import = run_process_import.delay(contents)
            redis_client.set(run_process_import.name, task_import.id)

        return RedirectResponse(
            url=request.url,
            status_code=303,
        )


async def get_template(model: BaseView, request: Request) -> _TemplateResponse:
    templates_map = {
        None: "import_excel.html",
        "PENDING": "import_process.html",
        "SUCCESS": "import_excel.html",
        "FAILURE": "import_error.html",
    }

    task_import = check_job_status(TASK_NAME)
    template = templates_map.get(
        getattr(task_import, "status", None), "import_excel.html"
    )

    context = {
        "request": request,
        "flash_message": (
            "Идет загрузка..."
            if task_import and task_import.status == "PENDING"
            else getattr(task_import, "info", None)
        ),
    }

    return await model.templates.TemplateResponse(
        request, name=template, context=context
    )
