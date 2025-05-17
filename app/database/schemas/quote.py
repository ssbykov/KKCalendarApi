from typing import Type

from pydantic import Field

from database import BaseSchema, BaseWithId, Quote


class QuoteSchemaCreate(BaseSchema):
    base_class: Type["BaseWithId"] = Field(default=Quote, exclude=True)
    text: str
    lama_id: int

    model_config = {"from_attributes": True}
