from typing import Any

from app.celery_worker import celery_app
from utils.quoters_import import process_import

TASK_NAME = "tasks.process_import"


@celery_app.task(name=TASK_NAME)  # type: ignore
def run_process_import(file_bytes: bytes) -> Any:
    import asyncio

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(process_import(file_bytes))
