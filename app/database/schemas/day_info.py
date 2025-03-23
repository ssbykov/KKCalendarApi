from datetime import datetime
from typing import Type, List, Optional

from pydantic import BaseModel, field_validator
from pydantic import Field
from sqlalchemy.orm import class_mapper

from database import (
    BaseWithId,
    Elements,
    SkylightArch,
    LaPosition,
    HaircuttingDay,
    Yelam,
    DayInfo,
)
from .base_schema import BaseSchema
from .event import EventSchema


class YelamSchema(BaseSchema):
    month: int = Field(ge=0, le=12)
    en_name: str = Field(max_length=20)
    ru_name: str = Field(max_length=20)
    base_class: Type[BaseWithId] = Field(default=Yelam, exclude=True)

    model_config = {"from_attributes": True}


class HaircuttingSchema(BaseSchema):
    moon_day: int = Field(ge=0, le=30)
    en_name: str = Field(max_length=100)
    ru_name: str = Field(max_length=100)
    is_inauspicious: bool
    base_class: Type[BaseWithId] = Field(default=HaircuttingDay, exclude=True)

    model_config = {"from_attributes": True}


class LaSchema(BaseSchema):
    moon_day: int = Field(ge=0, le=30)
    en_name: str = Field(max_length=40)
    ru_name: str = Field(max_length=40)
    base_class: Type[BaseWithId] = Field(default=LaPosition, exclude=True)

    model_config = {"from_attributes": True}


class ArchSchema(BaseSchema):
    moon_day: int = Field(ge=0, le=9)
    name: str = Field(max_length=10)
    en_desc: str = Field(max_length=100)
    ru_desc: str = Field(max_length=100)
    base_class: Type[BaseWithId] = Field(default=SkylightArch, exclude=True)

    model_config = {"from_attributes": True}


class ElementsSchema(BaseSchema):
    en_name: str = Field(max_length=100)
    ru_name: str = Field(max_length=100)
    ru_text: str
    en_text: str
    is_positive: bool
    base_class: Type[BaseWithId] = Field(default=Elements, exclude=True)

    model_config = {"from_attributes": True}


class DayInfoSchema(BaseModel):
    id: int
    date: str
    moon_day: str
    elements: ElementsSchema
    arch: ArchSchema
    la: LaSchema
    yelam: YelamSchema
    haircutting: HaircuttingSchema
    events: Optional[List["EventSchema"]]

    model_config = {"from_attributes": True}


class DayInfoSchemaCreate(BaseSchema):
    date: str
    moon_day: str
    elements_id: int
    arch_id: int
    la_id: int
    yelam_id: int
    haircutting_id: int
    events: Optional[List[int]]
    base_class: Type[BaseWithId] = Field(default=DayInfo, exclude=True)

    def to_orm(self) -> BaseWithId:
        column_names = list(self.base_class.__table__.columns.keys())
        column_names.remove("id")
        relationships = [
            column.key
            for column in class_mapper(self.base_class).relationships.values()
            if column.uselist
        ]
        dump = self.model_dump()
        if set(list(dump.keys())).issubset(set(column_names + relationships)):
            model = self.base_class(
                **{k: v for k, v in dump.items() if k not in relationships}
            )
            return model
        raise ValueError(
            "Параметры model_class не соответствуют параметрам базового класса."
        )

    @field_validator("date")
    def validate_date_format(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Дата должна быть в формате YYYY-MM-DD")
        return value
