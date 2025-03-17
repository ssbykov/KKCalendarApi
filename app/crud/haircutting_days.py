from crud.mixines import CommonMixin, GetBackNextIdMixin
from database import HaircuttingDay


class HaircuttingRepository(
    CommonMixin[HaircuttingDay], GetBackNextIdMixin[HaircuttingDay]
):
    model = HaircuttingDay
