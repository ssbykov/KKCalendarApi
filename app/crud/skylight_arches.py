from crud.mixines import GetBackNextIdMixin
from database import SkylightArch


class SkylightArchRepository(GetBackNextIdMixin[SkylightArch]):
    model = SkylightArch
