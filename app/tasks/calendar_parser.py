from typing import Any

from app.celery_worker import celery_app, CeleryTask
from app.utils.google_calendar_parser import calendar_parser_run

parser_task = CeleryTask("tasks.parser", calendar_parser_run)


@celery_app.task(name=parser_task.name)  # type: ignore
def run_process_parser(*args, **kwargs) -> Any:
    import asyncio

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(parser_task.func(*args, **kwargs))
