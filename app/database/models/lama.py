from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from . import BaseWithId


class Lama(BaseWithId):
    __tablename__ = "lamas"
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("event_photos.id"), nullable=True, unique=True
    )
    photo = relationship(
        "EventPhoto", uselist=False, back_populates=None, viewonly=True
    )

    def __str__(self) -> str:
        return self.name
