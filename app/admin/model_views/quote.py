from fastapi import HTTPException
from sqladmin import action, expose, BaseView
from sqladmin.templating import _TemplateResponse
from sqlalchemy import select, true, and_
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.admin.custom_model_view import CustomModelView
from app.admin.utils import check_superuser, text_formater
from app.celery_worker import redis_client, check_job_status
from app.database import Quote, db_helper
from app.database.crud.quotes import QuoteRepository
from app.tasks import run_process_import
from app.tasks.quoters import import_task
from app.utils.quoters_import import is_quote_unique


class QuoteAdmin(
    CustomModelView[Quote],
    model=Quote,
):
    repo_type = QuoteRepository
    name_plural = "Цитаты"
    name = "Цитата"
    icon = "fa-solid fa-quote-left"

    column_list = ("lama", "text")
    column_details_exclude_list = ("id", "lama_id")
    column_searchable_list = ("lama.name", "text")
    column_labels = {
        "text": "Цитата",
        "lama": "Автор",
        "created_at": "Добавлена",
    }
    can_edit = True
    can_delete = True
    can_export = False

    column_formatters_detail = text_formater(Quote)
    column_formatters = text_formater(Quote)

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
        pk = int(getattr(request, "path_params", {}).get("pk", -1)) if request else -1
        quote = form_data_dict.get("text", "").strip()
        lama_id = form_data_dict.get("lama")

        if not quote:
            return "Текст цитаты не может быть пустым"
        if not lama_id:
            return "Не указан автор цитаты"

        async for session in db_helper.get_session():
            # Сравниваем только с другими цитатами этого автора
            stmt = select(Quote.text).where(
                and_(
                    Quote.lama_id == int(lama_id),
                    Quote.id != pk if pk != -1 else true(),
                )
            )
            result = await session.execute(stmt)
            quotes_by_author = result.scalars().all()

            if not is_quote_unique(
                quote=quote,
                existing=quotes_by_author,
                new_quotes=set(),
            ):
                return "В базе уже есть цитата этого автора с совпадением более 75%"

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

        task = check_job_status(import_task.name)
        if task and task.status == "SUCCESS" or not task:
            content = await file.read()
            task_import = run_process_import.delay(content)
            redis_client.set(run_process_import.name, task_import.id)

        return RedirectResponse(
            url=request.url,
            status_code=303,
        )


async def get_template(model: BaseView, request: Request) -> _TemplateResponse:
    # Шаблон по умолчанию
    default_template = "import_excel.html"

    # Получаем статус задачи, если есть
    task_import = check_job_status(import_task.name)
    status = getattr(task_import, "status", "")

    # Определяем шаблон (если статус не в словаре — используем default)
    templates_map = {
        "PENDING": "import_process.html",
        "SUCCESS": default_template,
        "FAILURE": default_template,
    }
    template = templates_map.get(status, default_template)

    # Сообщения для разных статусов
    flash_messages = {
        "PENDING": "Идет загрузка...",
        "SUCCESS": getattr(task_import, "info", ""),
    }
    error_messages = {
        "FAILURE": f"Ошибка загрузки: {type(getattr(task_import, 'result', None))}, {status}",
    }

    context = {
        "request": request,
        "flash_message": flash_messages.get(status, ""),
        "error_message": error_messages.get(status, ""),
    }

    return await model.templates.TemplateResponse(
        request, name=template, context=context
    )
