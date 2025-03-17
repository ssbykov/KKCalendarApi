from crud.mixines import CommonMixin, GetBackNextIdMixin
from database import SkylightArch


class SkylightArchRepository(
    CommonMixin[SkylightArch], GetBackNextIdMixin[SkylightArch]
):
    model = SkylightArch
