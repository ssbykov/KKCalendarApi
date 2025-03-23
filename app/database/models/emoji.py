from sqlalchemy import String, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from . import BaseWithId


class Emoji(BaseWithId):
    __tablename__ = "emoji"
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    emoji: Mapped[str] = mapped_column(Unicode(10), nullable=False)

    def __str__(self) -> str:
        return f"{self.emoji} - {self.name}"
