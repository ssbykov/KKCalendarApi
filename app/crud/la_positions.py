from crud.mixines import GetBackNextIdMixin
from database import LaPosition


class LaPositionRepository(GetBackNextIdMixin[LaPosition]):
    model = LaPosition
