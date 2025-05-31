from database.crud.mixines import GetBackNextIdMixin
from database import Yelam


class YelamRepository(GetBackNextIdMixin[Yelam]):
    model = Yelam
