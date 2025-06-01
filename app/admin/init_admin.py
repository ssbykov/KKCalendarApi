import os
from datetime import datetime
from typing import Any, cast

from sqladmin import Admin
from sqladmin.authentication import login_required
from sqlalchemy.exc import IntegrityError
from starlette.datastructures import URL
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from app.core import settings
from app.database import db_helper, DayInfo
from app.database.backup_db import create_backup
from .backend import AdminAuth, owner_required
from .custom_model_view import CustomModelView
from .model_views import (
    EventAdmin,
    DayInfoAdmin,
    HaircuttingAdmin,
    ElementsAdmin,
    LaPositionAdmin,
    SkylightArchAdmin,
    YelamAdmin,
    EventPhotoAdmin,
    EventTypeAdmin,
    EmojiAdmin,
    BackupDbAdmin,
    UserAdmin,
    LamaAdmin,
    QuoteAdmin,
)
from .model_views.quote import QuoteView


async def init_admin(app: Any) -> None:
    admin = NewAdmin(
        app,
        db_helper.engine,
        title="Календарь событий",
        templates_dir=str(settings.sql_admin.templates),
        authentication_backend=AdminAuth(secret_key=settings.sql_admin.secret),
    )
    admin.add_view(DayInfoAdmin)
    admin.add_view(EventAdmin)
    admin.add_view(HaircuttingAdmin)
    admin.add_view(ElementsAdmin)
    admin.add_view(LaPositionAdmin)
    admin.add_view(SkylightArchAdmin)
    admin.add_view(YelamAdmin)
    admin.add_view(EventPhotoAdmin)
    admin.add_view(EventTypeAdmin)
    admin.add_view(EmojiAdmin)
    admin.add_view(LamaAdmin)
    admin.add_view(QuoteAdmin)
    admin.add_view(BackupDbAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(QuoteView)
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
        await db_helper.synch_backups()
        return RedirectResponse(request.url_for("admin:index"), status_code=302)

    @owner_required
    async def details(self, request: Request) -> Response:
        result = await super().details(request)
        if isinstance(result, RedirectResponse):
            return result
        context = result.context
        context["request"] = request
        return await self.templates.TemplateResponse(request, result.template, context)

    @owner_required
    async def edit(self, request: Request) -> Response:
        """Edit model endpoint."""

        await self._edit(request)
        identity = request.path_params["identity"]
        model_view = self._find_custom_model_view(identity)

        model = await model_view.get_object_for_edit(request)
        if not model:
            raise HTTPException(status_code=404)

        Form = await model_view.scaffold_form(model_view._form_edit_rules)
        context = {
            "obj": model,
            "model_view": model_view,
            "form": Form(obj=model, data=self._normalize_wtform_data(model)),
        }

        if request.method == "GET":
            return await self.templates.TemplateResponse(
                request, model_view.edit_template, context
            )

        form_data = await self._handle_form_data(request, model)
        form = Form(form_data)
        form_data_dict = self._denormalize_wtform_data(form.data, model)

        if not form.validate():
            context["error"] = "Пожалуйста, исправьте ошибки в форме."
            context["errors"] = form.errors

        else:
            try:
                if isinstance(model_view, LamaAdmin) and not form_data_dict.get(
                    "photo"
                ):
                    form_data_dict["photo_id"] = None

                restriction = await model_view.check_restrictions_create(
                    form_data_dict, request
                )

                if restriction:
                    context["error"] = restriction
                else:
                    pk = request.path_params["pk"]
                    obj = await model_view.update_model(
                        request, pk=pk, data=form_data_dict
                    )

                    url = self.get_save_redirect_url(
                        request=request,
                        form=form_data,
                        obj=obj,
                        model_view=model_view,
                    )
                    response = RedirectResponse(url=url, status_code=302)

                    if isinstance(response, RedirectResponse):
                        if hasattr(model_view, "get_page_for_url"):
                            if page_suffix := await model_view.get_page_for_url(
                                request
                            ):
                                response.headers["location"] += page_suffix
                        return response

            except Exception as e:
                context["error"] = str(e)
        return await self.templates.TemplateResponse(
            request, model_view.edit_template, context, status_code=400
        )

    def _find_custom_model_view(self, identity: str) -> CustomModelView[Any]:
        return cast(CustomModelView[Any], self._find_model_view(identity))

    @owner_required
    async def delete(self, request: Request) -> Response:
        identity = request.path_params["identity"]
        model_view = self._find_custom_model_view(identity)

        restriction = await model_view.check_restrictions_delete(request)

        if restriction:
            raise HTTPException(detail=restriction, status_code=409)

        if isinstance(model_view, BackupDbAdmin):
            backup_id = int(request.query_params["pks"])
            if backup_db := await model_view.get_by_id(backup_id):
                file_path = os.path.join(settings.db.backups_dir, backup_db.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
        try:
            result = await super().delete(request)
            return cast(Response, result)
        except Exception as e:
            if isinstance(e, IntegrityError):
                restriction = "Данная запись не может быть удалена из на нарушения целостности базы."
            else:
                restriction = str(e)
            return Response(
                status_code=409,
                content=restriction,
            )

    @login_required
    async def create(self, request: Request) -> Response:
        await self._create(request)

        identity = request.path_params["identity"]
        model_view = self._find_custom_model_view(identity)

        if isinstance(model_view, BackupDbAdmin):
            await create_backup()
            url = request.url_for("admin:list", identity=identity)
            return RedirectResponse(url=url, status_code=302)

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
            context["error"] = "Пожалуйста, исправьте ошибки в форме."
            context["errors"] = form.errors
        else:
            form_data_dict = self._denormalize_wtform_data(form.data, model_view.model)
            try:

                restriction = await model_view.check_restrictions_create(form_data_dict)
                if restriction:
                    raise ValueError(restriction)

                obj = await model_view.insert_model(request, form_data_dict)
                url = cast(
                    URL,
                    self.get_save_redirect_url(
                        request=request,
                        form=form_data,
                        obj=obj,
                        model_view=model_view,
                    ),
                )
                return RedirectResponse(url=url, status_code=302)

            except Exception as e:
                context["error"] = str(e)
                if "days" in form_data_dict:
                    form_data_dict["days"] = []
                form.process(**form_data_dict)

        return await self.templates.TemplateResponse(
            request, model_view.create_template, context, status_code=400
        )


def get_past_days_ids(days: list[DayInfo]) -> list[str]:
    return sorted(
        str(day.id)
        for day in days
        if datetime.strptime(day.date, "%Y-%m-%d") <= datetime.now()
    )
