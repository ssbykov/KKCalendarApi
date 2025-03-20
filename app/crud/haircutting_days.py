from crud.mixines import GetBackNextIdMixin
from database import HaircuttingDay


class HaircuttingRepository(GetBackNextIdMixin[HaircuttingDay]):
    model = HaircuttingDay
