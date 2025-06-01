from app.database.crud.mixines import GetBackNextIdMixin
from app.database import Yelam


class YelamRepository(GetBackNextIdMixin[Yelam]):
    model = Yelam
