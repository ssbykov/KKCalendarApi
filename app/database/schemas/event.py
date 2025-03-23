from typing import Type

from pydantic import Field

from database import BaseSchema, Event, BaseWithId


class EventSchema(BaseSchema):
    name: str
    moon_day: str | None = None
    en_name: str
    ru_name: str
    en_text: str | None = None
    ru_text: str | None = None
    link: str | None = None
    user_id: int | None
    photo_id: int | None = None
    type_id: int | None = None


class EventSchemaCreate(EventSchema):
    base_class: Type["BaseWithId"] = Field(default=Event, exclude=True)

    model_config = {"from_attributes": True}
