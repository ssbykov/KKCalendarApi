from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore
from celery import chain  # type: ignore

from app.core import settings
from app.tasks.calendar_parser import run_process_parser
from app.tasks.send_email import run_process_mail

scheduler = AsyncIOScheduler()


async def check_calendar_update() -> None:
    parser_task = run_process_parser.s(period=12, update=False)
    context = {
        "user_email": settings.super_user.email,
    }
    send_mail_task = run_process_mail.s(context=context, action="check_update")
    chain(parser_task, send_mail_task)()


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
