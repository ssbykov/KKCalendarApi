from typing import Type, TYPE_CHECKING

from pydantic import Field

from database import Event, BaseWithId
from .day_info import DayDataSchema


class EventSchema(DayDataSchema):
    name: str
    moon_day: str | None = None
    en_name: str
    ru_name: str | None = None
    en_text: str | None = None
    ru_text: str | None = None
    link: str | None = None


class EventSchemaCreate(EventSchema):
    base_class: Type[BaseWithId] = Field(default=Event, exclude=True)
    is_mutable: bool = False

    model_config = {"from_attributes": True}
