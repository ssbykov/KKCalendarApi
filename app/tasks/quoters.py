from typing import Any

from app.celery_worker import CeleryTask
from app.celery_worker import celery_app
from app.utils.quoters_import import process_import

import_task = CeleryTask("tasks.import", process_import)


@celery_app.task(name=import_task.name)  # type: ignore
def run_process_import(*args: Any) -> Any:
    import asyncio

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(import_task.func(*args))
