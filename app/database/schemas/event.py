from typing import Type

from pydantic import Field, BaseModel

from app.database import Event, BaseWithId
from .base_schema import BaseSchema


class EventTypeSchema(BaseModel):
    name: str
    description: str | None = None
    rank: int

    class Config:
        from_attributes = True


class EmojiSchema(BaseModel):
    name: str
    emoji: str | None = None

    class Config:
        from_attributes = True


class EventSchemaBase(BaseSchema):
    name: str
    moon_date: str | None = None
    en_name: str
    ru_name: str
    en_text: str | None = None
    ru_text: str | None = None
    link: str | None = None
    photo_id: int | None = None


class EventSchema(EventSchemaBase):
    type: EventTypeSchema | None = None
    emoji: EmojiSchema | None = None

    model_config = {"from_attributes": True}


class EventSchemaCreate(EventSchemaBase):
    base_class: Type["BaseWithId"] = Field(default=Event, exclude=True)
    user_id: int | None
    type_id: int | None = None
    emoji_id: int | None = None

    model_config = {"from_attributes": True}
