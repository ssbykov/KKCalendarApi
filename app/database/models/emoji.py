from sqlalchemy import String, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from . import BaseWithId


class Emoji(BaseWithId):
    """
    Модель для хранения эмодзи и их названий.
    
    Используется для создания справочника эмодзи с их текстовыми названиями.
    Каждый эмодзи имеет уникальное название и соответствующий Unicode символ.
    
    Attributes:
        name (str): Уникальное название эмодзи (до 50 символов).
        emoji (str): Unicode символ эмодзи (до 10 символов).
    """
    __tablename__ = "emoji"
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    emoji: Mapped[str] = mapped_column(Unicode(10), nullable=False)

    def __str__(self) -> str:
        return f"{self.emoji} - {self.name}"
