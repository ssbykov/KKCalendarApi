from database.crud.mixines import GetBackNextIdMixin
from database import Elements


class ElementsRepository(GetBackNextIdMixin[Elements]):
    model = Elements
