from typing import Type

from pydantic import Field

from database import BaseSchema, BaseWithId, TaskScheduler, Advertisement


class TaskSchema(BaseSchema):
    base_class: Type["BaseWithId"] = Field(default=TaskScheduler, exclude=True)
    hour: int
    minute: int
    days: str
    timezone: str
    advertisement: "AdvertisementSchema"

    model_config = {"from_attributes": True}


class AdvertisementSchema(BaseSchema):
    base_class: Type["BaseWithId"] = Field(default=Advertisement, exclude=True)
    name: str
    caption: str
    ids: dict
    image_id: int

    model_config = {"from_attributes": True}
