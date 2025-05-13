from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from . import BaseWithId


class Quote(BaseWithId):
    __tablename__ = "quotes"
    text: Mapped[str] = mapped_column(Text, nullable=True)
    lama_id: Mapped[int] = mapped_column(ForeignKey("lamas.id"), nullable=False)
    lama = relationship("Lama", backref=backref("lama"))

    def __str__(self) -> str:
        return self.text
