from app.database.crud.mixines import GetBackNextIdMixin
from app.database import TaskScheduler


class TaskRepository(GetBackNextIdMixin[TaskScheduler]):
    model = TaskScheduler
