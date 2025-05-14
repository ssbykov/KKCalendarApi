from crud.mixines import GetBackNextIdMixin
from database import Lama


class LamaRepository(GetBackNextIdMixin[Lama]):
    model = Lama

    async def check_photo(self, photo_id: int) -> bool:
        stmt = self.main_stmt.where(self.model.photo_id == photo_id)
        result = await self.session.scalar(stmt)
        return bool(result)
