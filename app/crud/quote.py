from crud.mixines import GetBackNextIdMixin
from database import Quote


class QuoteRepository(GetBackNextIdMixin[Quote]):
    model = Quote
