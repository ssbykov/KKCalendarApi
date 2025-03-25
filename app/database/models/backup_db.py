from sqlalchemy import String, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from . import BaseWithId


class BackupDb(BaseWithId):
    __tablename__ = "backups"
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    def __str__(self) -> str:
        return self.name
