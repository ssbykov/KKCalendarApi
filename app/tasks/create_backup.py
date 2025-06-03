from typing import Any

from celery_worker import celery_app
from database.backup_db import create_backup

TASK_NAME = "tasks.process_backup"


@celery_app.task(name=TASK_NAME)  # type: ignore
def run_process_backup() -> Any:
    import asyncio

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(create_backup())
