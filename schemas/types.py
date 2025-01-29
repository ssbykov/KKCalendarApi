from datetime import datetime

from pydantic import BaseModel, field_validator


class DateSchema(BaseModel):
    date: str

    @field_validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Неправильный формат даты. Используйте YYYY-MM-DD')
        return v