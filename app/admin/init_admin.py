from datetime import datetime
from typing import Any, cast

from sqladmin import Admin, ModelView
from sqladmin.authentication import login_required
from sqladmin.helpers import get_object_identifier
from sqlalchemy.exc import IntegrityError
from starlette.datastructures import FormData, URL
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from core import settings
from crud.days_info import DayInfoRepository
from database import db_helper, DayInfo
from .backend import AdminAuth, owner_required
from .model_views import EventAdmin, DayInfoAdmin


async def init_admin(app: Any) -> None:
    admin = NewAdmin(
        app,
        db_helper.engine,
        title="Календарь событий",
        templates_dir=settings.sql_admin.templates,
        authentication_backend=AdminAuth(secret_key=settings.sql_admin.secret),
    )
    admin.add_view(DayInfoAdmin)
    admin.add_view(EventAdmin)
    assert isinstance(admin.authentication_backend, AdminAuth)
    await admin.authentication_backend.create_superuser()


class NewAdmin(Admin):
    async def login(self, request: Request) -> Response:
        assert isinstance(self.authentication_backend, AdminAuth)

        context: dict[str, str | None] = {}
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "sqladmin/login.html")

        response = await self.authentication_backend.login_with_info(request)
        if not response.is_ok:
            context["error"] = response.error
            context["message"] = response.message
            return await self.templates.TemplateResponse(
                request, "sqladmin/login.html", context, status_code=400
            )

        return RedirectResponse(request.url_for("admin:index"), status_code=302)

    @owner_required
    async def details(self, request: Request) -> Response:
        result = await super().details(request)
        context = result.context
        context["request"] = request
        return await self.templates.TemplateResponse(request, result.template, context)

    @owner_required
    async def edit(self, request: Request) -> Response:
        """Edit model endpoint."""

        await self._edit(request)

        identity = request.path_params["identity"]
        model_view = self._find_model_view(identity)

        model = await model_view.get_object_for_edit(request)
        if not model:
            raise HTTPException(status_code=404)

        Form = await model_view.scaffold_form(model_view._form_edit_rules)
        context = {
            "obj": model,
            "model_view": model_view,
            "form": Form(obj=model, data=self._normalize_wtform_data(model)),
            "error": request.session.pop("error", None),
        }

        if request.method == "GET":
            return await self.templates.TemplateResponse(
                request, model_view.edit_template, context
            )

        form_data = await self._handle_form_data(request, model)
        form = Form(form_data)

        if isinstance(model_view, EventAdmin):
            past_days_in_model: list[str] = get_past_days_ids(model.days)

            past_days_in_form = await filter_past_days_by_id(form.data.get("days", []))

            if past_days_in_form != past_days_in_model:
                context["error"] = "Нельзя изменить или добавить прошедшие даты"
                return await self.templates.TemplateResponse(
                    request, model_view.edit_template, context, status_code=400
                )

        if not form.validate():
            context["form"] = form
            return await self.templates.TemplateResponse(
                request, model_view.edit_template, context, status_code=400
            )

        form_data_dict = self._denormalize_wtform_data(form.data, model)
        try:
            obj = await model_view.update_model(
                request, pk=request.path_params["pk"], data=form_data_dict
            )

        except IntegrityError:
            if isinstance(
                model_view, EventAdmin
            ) and await model_view.get_event_by_name(form_data_dict.get("name", "")):
                context["error"] = "Данное название уже используется"
                return await self.templates.TemplateResponse(
                    request, model_view.edit_template, context, status_code=400
                )
            else:
                raise
        except Exception as e:
            context["error"] = str(e)
            return await self.templates.TemplateResponse(
                request, model_view.edit_template, context, status_code=400
            )

        url = self.get_save_redirect_url(
            request=request,
            form=form_data,
            obj=obj,
            model_view=model_view,
        )
        response = RedirectResponse(url=url, status_code=302)
        if isinstance(response, RedirectResponse):
            if hasattr(model_view, "get_page_for_url") and (
                page_suffix := await model_view.get_page_for_url(request)
            ):
                response.headers["location"] += page_suffix
                return response
        return cast(Response, response)

    @owner_required
    async def delete(self, request: Request) -> Response:
        identity = request.path_params["identity"]
        model_view = self._find_model_view(identity)

        if isinstance(model_view, EventAdmin):
            event = await model_view.get_event(request)
            if get_past_days_ids(event.days):
                return Response(
                    status_code=404,
                    content="Нельзя удалить событие с прошедшими датами",
                )
        result = await super().delete(request)
        return cast(Response, result)

    @login_required
    async def create(self, request: Request) -> Response:
        await self._create(request)

        identity = request.path_params["identity"]
        model_view = self._find_model_view(identity)

        Form = await model_view.scaffold_form(model_view._form_create_rules)
        form_data = await self._handle_form_data(request)
        form = Form(form_data)

        context = {
            "model_view": model_view,
            "form": form,
        }

        if request.method == "GET":
            return await self.templates.TemplateResponse(
                request, model_view.create_template, context
            )

        if not form.validate():
            return await self.templates.TemplateResponse(
                request, model_view.create_template, context, status_code=400
            )

        form_data_dict = self._denormalize_wtform_data(form.data, model_view.model)
        try:
            if isinstance(model_view, EventAdmin) and await filter_past_days_by_id(
                form_data_dict.get("days", [])
            ):
                form_data_dict["days"] = []
                context["error"] = "Нельзя изменить или добавить прошедшие даты"
                request.session["error"] = context["error"]

            obj = await model_view.insert_model(request, form_data_dict)
        except IntegrityError:
            if isinstance(
                model_view, EventAdmin
            ) and await model_view.get_event_by_name(form_data_dict.get("name", "")):
                context["error"] = "Данное название уже используется"
                return await self.templates.TemplateResponse(
                    request,
                    context["model_view"].create_template,
                    context,
                    status_code=400,
                )
            else:
                raise

        except Exception as e:
            context["error"] = str(e)
            return await self.templates.TemplateResponse(
                request, context["model_view"].create_template, context, status_code=400
            )

        url = self.get_save_redirect_url(
            request=request,
            form=form_data,
            obj=obj,
            model_view=model_view,
        )
        return RedirectResponse(url=url, status_code=302)

    def get_save_redirect_url(
        self, request: Request, form: FormData, model_view: ModelView, obj: Any
    ) -> str | URL:

        identity = request.path_params["identity"]
        identifier = get_object_identifier(obj)

        if request.session.get("error"):
            return request.url_for("admin:edit", identity=identity, pk=identifier)
        else:
            return request.url_for("admin:list", identity=identity)


async def filter_past_days_by_id(day_ids: list[str]) -> list[str]:
    past_days = []
    for day_id in day_ids:
        async for session in db_helper.get_session():
            repo = DayInfoRepository(session)
            day_info = await repo.get_day_by_id(day_id)
            if datetime.strptime(day_info.date, "%Y-%m-%d") <= datetime.now():
                past_days.append(day_id)
    return sorted(past_days)


def get_past_days_ids(days: list[DayInfo]) -> list[str]:
    return sorted(
        str(day.id)
        for day in days
        if datetime.strptime(day.date, "%Y-%m-%d") <= datetime.now()
    )
