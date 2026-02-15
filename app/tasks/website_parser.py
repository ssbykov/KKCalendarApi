from typing import Any

from app.celery_worker import celery_app, CeleryTask
from app.utils.http_calendar_parser import calendar_parser_run

web_parser_task = CeleryTask("tasks.website_parser", calendar_parser_run)


@celery_app.task(name=web_parser_task.name)  # type: ignore
def run_website_process_parser(*args: Any, **kwargs: Any) -> Any:
    import asyncio

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(web_parser_task.func(*args, **kwargs))
