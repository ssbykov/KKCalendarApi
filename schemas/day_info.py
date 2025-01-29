from datetime import datetime
from typing import Type, List, Optional

from pydantic import BaseModel, field_validator
from pydantic import Field
from sqlalchemy.orm import class_mapper

from database.database import Base
from models.day_info import (
    DescriptionModel,
    ElementModel,
    ArchModel,
    LaModel,
    HaircuttingModel,
    YelamModel,
    DayInfo,
)


class DayDataSchema(BaseModel):
    base_class: Type[Base] = Field(default=Base, exclude=True)

    def to_orm(self) -> Base:
        column_names = list(self.base_class.__table__.columns.keys())
        column_names.remove("id")
        if column_names == list(self.model_dump().keys()):
            return self.base_class(**self.model_dump())
        raise ValueError(
            "Параметры model_class не соответствуют параметрам базового класса."
        )


class YelamSchema(DayDataSchema):
    month: int = Field(ge=0, le=12)
    en_name: str = Field(max_length=20)
    ru_name: str = Field(max_length=20)
    base_class: Type[Base] = Field(default=YelamModel, exclude=True)

    model_config = {"from_attributes": True}


class HaircuttingSchema(DayDataSchema):
    moon_day: int = Field(ge=0, le=30)
    en_name: str = Field(max_length=100)
    ru_name: str = Field(max_length=100)
    is_inauspicious: bool
    base_class: Type[Base] = Field(default=HaircuttingModel, exclude=True)

    model_config = {"from_attributes": True}


class LaSchema(DayDataSchema):
    moon_day: int = Field(ge=0, le=30)
    en_name: str = Field(max_length=40)
    ru_name: str = Field(max_length=40)
    base_class: Type[Base] = Field(default=LaModel, exclude=True)

    model_config = {"from_attributes": True}


class ArchSchema(DayDataSchema):
    moon_day: int = Field(ge=0, le=9)
    name: str = Field(max_length=10)
    en_desc: str = Field(max_length=100)
    ru_desc: str = Field(max_length=100)
    base_class: Type[Base] = Field(default=ArchModel, exclude=True)

    model_config = {"from_attributes": True}


class ElementSchema(DayDataSchema):
    name: str = Field(max_length=40)
    base_class: Type[Base] = Field(default=ElementModel, exclude=True)

    model_config = {"from_attributes": True}


class DescriptionSchema(DayDataSchema):
    id: int
    text: str
    link: str
    day_info_id: int

    model_config = {"from_attributes": True}


class DayInfoSchema(BaseModel):
    id: int
    date: str
    moon_day: str
    first_element: ElementSchema
    second_element: ElementSchema
    arch: ArchSchema
    la: LaSchema
    yelam: YelamSchema
    haircutting: HaircuttingSchema
    descriptions: List[DescriptionSchema]

    model_config = {"from_attributes": True}


class ParthDescriptionSchema(DayDataSchema):
    text: str
    link: str
    base_class: Type[Base] = Field(default=DescriptionModel, exclude=True)

    model_config = {"from_attributes": True}


class ParthDayInfoSchema(DayDataSchema):
    date: str
    moon_day: str
    first_element_id: int
    second_element_id: int
    arch_id: int
    la_id: int
    yelam_id: int
    haircutting_id: int
    descriptions: Optional[List[ParthDescriptionSchema]]
    base_class: Type[Base] = Field(default=DayInfo, exclude=True)

    def to_orm(self) -> Base:
        column_names = list(self.base_class.__table__.columns.keys())
        column_names.remove("id")
        relationships = [
            column.key
            for column in class_mapper(self.base_class).relationships.values()
            if column.uselist
        ]
        if column_names + relationships == list(self.model_dump().keys()):
            dump = {
                k: v for k, v in self.model_dump().items() if k not in relationships
            }
            model = self.base_class(**dump)
            for relationship in relationships:
                attribute = getattr(self, relationship)
                if attribute:
                    relationship_class = attribute[0].base_class
                    for relationship_dump in self.model_dump().get(relationship, []):
                        getattr(model, relationship).append(
                            relationship_class(**relationship_dump)
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
