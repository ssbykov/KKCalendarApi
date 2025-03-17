from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from . import BaseWithId


class EventPhoto(BaseWithId):
    __tablename__ = "photos"
    en_name: Mapped[str] = mapped_column(String(30), nullable=False)
    photo_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
