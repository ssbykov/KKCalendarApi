from crud.mixines import GetBackNextIdMixin
from database import Lama


class LamaRepository(GetBackNextIdMixin[Lama]):
    model = Lama
