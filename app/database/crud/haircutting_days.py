from app.database.crud.mixines import GetBackNextIdMixin
from app.database import HaircuttingDay


class HaircuttingRepository(GetBackNextIdMixin[HaircuttingDay]):
    model = HaircuttingDay
