from typing import Type

from pydantic import Field, BaseModel

from database import Event, BaseWithId
from .base_schema import BaseSchema


class EventTypeSchema(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class EventSchema(BaseSchema):
    name: str
    moon_day: str | None = None
    en_name: str
    ru_name: str
    en_text: str | None = None
    ru_text: str | None = None
    link: str | None = None
    photo_id: int | None = None
    type: EventTypeSchema | None = None

    class Config:
        from_attributes = True


class EventSchemaCreate(EventSchema):
    base_class: Type["BaseWithId"] = Field(default=Event, exclude=True)
    user_id: int | None
    type_id: int | None = None

    model_config = {"from_attributes": True}
