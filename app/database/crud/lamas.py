from sqlalchemy import func

from app.database.crud.mixines import GetBackNextIdMixin
from app.database import Lama
from app.database.schemas.lama import LamaSchemaCreate


class LamaRepository(GetBackNextIdMixin[Lama]):
    model = Lama

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

    async def get_lama_by_photo(self, photo_id: int) -> Lama | None:
        stmt = self.main_stmt.where(self.model.photo_id == photo_id)
        lama = await self.session.scalar(stmt)
        if lama:
            return lama
        return None
