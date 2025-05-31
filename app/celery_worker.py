from celery import Celery

celery_app = Celery(
    "kkcalendar", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)

celery_app.autodiscover_tasks(["app.tasks"])
import app.tasks
