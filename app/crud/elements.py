from crud.mixines import CommonMixin, GetBackNextIdMixin
from database import Elements


class ElementsRepository(CommonMixin[Elements], GetBackNextIdMixin[Elements]):
    model = Elements
