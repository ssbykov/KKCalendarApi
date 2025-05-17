from sqlalchemy import func

from crud.mixines import GetBackNextIdMixin
from database import Lama
from database.schemas.lama import LamaSchemaCreate


class LamaRepository(GetBackNextIdMixin[Lama]):
    model = Lama

    async def check_photo(self, photo_id: int) -> bool:
        stmt = self.main_stmt.where(self.model.photo_id == photo_id)
        result = await self.session.scalar(stmt)
        return bool(result)

    async def add_lama(self, lama: LamaSchemaCreate) -> int:
        orm_lama = lama.to_orm()
        self.session.add(orm_lama)
        await self.session.flush()
        lama_id = orm_lama.id
        await self.session.commit()
        return lama_id

    async def get_lama_by_name(self, name: str) -> Lama | None:
        stmt = self.main_stmt.where(func.upper(self.model.name) == func.upper(name))
        lama = await self.session.scalar(stmt)
        if lama:
            return lama
        return None
