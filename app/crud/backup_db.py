from crud.mixines import GetBackNextIdMixin
from database import BackupDb


class BackupDbRepository(GetBackNextIdMixin[BackupDb]):
    model = BackupDb
