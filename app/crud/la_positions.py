from crud.mixines import CommonMixin, GetBackNextIdMixin
from database import LaPosition


class LaPositionRepository(CommonMixin[LaPosition], GetBackNextIdMixin[LaPosition]):
    model = LaPosition
