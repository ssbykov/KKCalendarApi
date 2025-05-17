from typing import Type

from pydantic import Field

from database import BaseSchema, Lama, BaseWithId


class LamaSchemaCreate(BaseSchema):
    base_class: Type["BaseWithId"] = Field(default=Lama, exclude=True)
    name: str
    description: str | None = None
    photo_id: int | None = None

    model_config = {"from_attributes": True}
