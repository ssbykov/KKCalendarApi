from crud.mixines import CommonMixin, GetBackNextIdMixin
from database import SkylightArch, Yelam


class YelamRepository(CommonMixin[Yelam], GetBackNextIdMixin[Yelam]):
    model = Yelam
