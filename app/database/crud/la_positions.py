from app.database.crud.mixines import GetBackNextIdMixin
from app.database import LaPosition


class LaPositionRepository(GetBackNextIdMixin[LaPosition]):
    model = LaPosition
