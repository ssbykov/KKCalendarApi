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
    Event,
)


class DayDataSchema(BaseModel):
    """
    Базовый класс для схем, которые могут быть преобразованы в ORM-модели.
    """

    base_class: Type[BaseWithId] = Field(default=BaseWithId, exclude=True)

    def to_orm(self) -> BaseWithId:
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
    base_class: Type[BaseWithId] = Field(default=Yelam, exclude=True)

    model_config = {"from_attributes": True}


class HaircuttingSchema(DayDataSchema):
    moon_day: int = Field(ge=0, le=30)
    en_name: str = Field(max_length=100)
    ru_name: str = Field(max_length=100)
    is_inauspicious: bool
    base_class: Type[BaseWithId] = Field(default=HaircuttingDay, exclude=True)

    model_config = {"from_attributes": True}


class LaSchema(DayDataSchema):
    moon_day: int = Field(ge=0, le=30)
    en_name: str = Field(max_length=40)
    ru_name: str = Field(max_length=40)
    base_class: Type[BaseWithId] = Field(default=LaPosition, exclude=True)

    model_config = {"from_attributes": True}


class ArchSchema(DayDataSchema):
    moon_day: int = Field(ge=0, le=9)
    name: str = Field(max_length=10)
    en_desc: str = Field(max_length=100)
    ru_desc: str = Field(max_length=100)
    base_class: Type[BaseWithId] = Field(default=SkylightArch, exclude=True)

    model_config = {"from_attributes": True}


class ElementsSchema(DayDataSchema):
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


class DayInfoSchemaCreate(DayDataSchema):
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


class EventSchema(DayDataSchema):
    name: str
    moon_day: str | None = None
    en_name: str
    ru_name: str | None = None
    en_text: str | None = None
    ru_text: str | None = None
    link: str | None = None


class EventSchemaCreate(EventSchema):
    base_class: Type["BaseWithId"] = Field(default=Event, exclude=True)
    is_mutable: bool = False

    model_config = {"from_attributes": True}
