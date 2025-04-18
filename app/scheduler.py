from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore

from core import settings
from utils.email_sender import send_email
from utils.google_calendar_parser import calendar_parser_run

scheduler = AsyncIOScheduler()


async def check_calendar_update() -> None:
    result = await calendar_parser_run(period=12, update=False)
    context: dict[str, Any] = {
        "user_email": settings.super_user.email,
        "update_result": result,
    }
    await send_email(
        action="check_update",
        context=context,
    )


async def startup_scheduler() -> None:
    # Настраиваем задачу на выполнение каждый день в 7 утра по Москве
    scheduler.add_job(
        check_calendar_update,
        CronTrigger(
            hour=9,
            minute=0,
            timezone="Europe/Moscow",  # Указываем московский часовой пояс
        ),
        misfire_grace_time=60,  # Допустимое время задержки (секунды)
    )

    # Запускаем планировщик
    scheduler.start()


async def shutdown_scheduler() -> None:
    scheduler.shutdown()
