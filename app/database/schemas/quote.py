from typing import Type

from pydantic import Field

from app.database import BaseSchema, BaseWithId, Quote
from app.database.schemas.lama import LamaSchemaCreate


class QuoteSchemaBase(BaseSchema):
    base_class: Type["BaseWithId"] = Field(default=Quote, exclude=True)
    text: str

    model_config = {"from_attributes": True}


class QuoteSchemaCreate(QuoteSchemaBase):
    lama_id: int


class QuoteSchema(QuoteSchemaBase):
    lama: LamaSchemaCreate
