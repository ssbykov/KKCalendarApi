from datetime import datetime
from typing import Type, List, Optional

from pydantic import BaseModel, field_validator
from pydantic import Field
from sqlalchemy.orm import class_mapper

from database import (
    Base,
    DescriptionModel,
    ElementModel,
    ArchModel,
    LaModel,
    HaircuttingModel,
    YelamModel,
    DayInfo,
)


class DayDataSchema(BaseModel):
    """
    Базовый класс для схем, которые могут быть преобразованы в ORM-модели.
    """

    base_class: Type[Base] = Field(default=Base, exclude=True)

    def to_orm(self) -> Base:
        """
        Преобразует схему в ORM-модель.
        """
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


class DescriptionSchemaBase(DayDataSchema):
    text: str
    link: str


class DescriptionSchema(DescriptionSchemaBase):
    id: int
    day_info_id: int

    model_config = {"from_attributes": True}


class DescriptionSchemaCreate(DescriptionSchemaBase):
    base_class: Type[Base] = Field(default=DescriptionModel, exclude=True)

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


class DayInfoSchemaCreate(DayDataSchema):
    date: str
    moon_day: str
    first_element_id: int
    second_element_id: int
    arch_id: int
    la_id: int
    yelam_id: int
    haircutting_id: int
    descriptions: Optional[List[DescriptionSchemaCreate]]
    base_class: Type[Base] = Field(default=DayInfo, exclude=True)

    def to_orm(self) -> Base:
        column_names = list(self.base_class.__table__.columns.keys())
        column_names.remove("id")
        relationships = [
            column.key
            for column in class_mapper(self.base_class).relationships.values()
            if column.uselist
        ]
        dump = self.model_dump()
        if column_names + relationships == list(dump.keys()):
            model = self.base_class(
                **{k: v for k, v in dump.items() if k not in relationships}
            )
            for relationship in relationships:
                attribute = getattr(self, relationship)
                if attribute:
                    relationship_class = attribute[0].base_class
                    for relationship_dump in dump.get(relationship, []):
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
