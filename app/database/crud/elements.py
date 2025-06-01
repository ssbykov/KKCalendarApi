from app.database.crud.mixines import GetBackNextIdMixin
from app.database import Elements


class ElementsRepository(GetBackNextIdMixin[Elements]):
    model = Elements
