from datetime import datetime

from sqlalchemy import Column, String, DateTime

from .base import Base


class YandexToken(Base):
    __tablename__ = "yandex_tokens"
    id = Column(String, primary_key=True, default="main")
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # когда истекает access_token
    updated_at = Column(DateTime, default=datetime.now())
