from pathlib import Path

from starlette.exceptions import HTTPException
from starlette.responses import FileResponse

from crud.mixines import CommonMixin, GetBackNextIdMixin
from database import SessionDep
from database.models import EventPhoto


def get_event_photos_repository(session: SessionDep) -> "EventPhotoRepository":
    return EventPhotoRepository(session)


class EventPhotoRepository(CommonMixin[EventPhoto], GetBackNextIdMixin[EventPhoto]):
    model = EventPhoto

    async def get_photo_by_id(self, photo_id: int) -> FileResponse | HTTPException:
        stmt = self.main_stmt.where(self.model.id == photo_id)
        photo = await self.session.scalar(stmt)
        if photo and Path(photo.photo_data):
            return FileResponse(photo.photo_data)
        return HTTPException(status_code=404, detail="File not found")
