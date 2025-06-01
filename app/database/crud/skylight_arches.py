from app.database.crud.mixines import GetBackNextIdMixin
from app.database import SkylightArch


class SkylightArchRepository(GetBackNextIdMixin[SkylightArch]):
    model = SkylightArch
