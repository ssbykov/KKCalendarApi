from typing import Type

from pydantic import BaseModel
from pydantic import Field

from database.database import Base


class DayDataSchema(BaseModel):
    def to_orm(self, model_class: Type[Base]) -> Base:
        column_names = [column.name for column in model_class.__table__.columns if column.name != "id"]
        if column_names == list(self.dict().keys()):
            return model_class(**self.dict())
        raise ValueError("Параметры model_class не соответствуют параметрам базового класса.")


class YelamSchema(DayDataSchema):
    month: int = Field(ge=0, le=12)
    en_name: str = Field(max_length=20)
    ru_name: str = Field(max_length=20)

    model_config = {
        "from_attributes": True
    }


class HaircuttingSchema(DayDataSchema):
    moon_day: int = Field(ge=0, le=30)
    en_name: str = Field(max_length=50)
    ru_name: str = Field(max_length=50)
    is_inauspicious: bool

    model_config = {
        "from_attributes": True
    }


class LaSchema(DayDataSchema):
    moon_day: int = Field(ge=0, le=30)
    en_name: str = Field(max_length=40)
    ru_name: str = Field(max_length=40)

    model_config = {
        "from_attributes": True
    }


class ArchSchema(DayDataSchema):
    moon_day: int = Field(ge=0, le=9)
    name: str = Field(max_length=10)
    en_desc: str = Field(max_length=100)
    ru_desc: str = Field(max_length=100)

    model_config = {
        "from_attributes": True
    }


class ElementSchema(DayDataSchema):
    name: str = Field(max_length=40)

    model_config = {
        "from_attributes": True
    }


class DayInfoSchema(DayDataSchema):
    id: int
    date: str
    moon_day: str
    first_element: ElementSchema
    second_element: ElementSchema
    arch: ArchSchema
    la: LaSchema
    yelam: YelamSchema
    haircutting: HaircuttingSchema

    model_config = {
        "from_attributes": True
    }
