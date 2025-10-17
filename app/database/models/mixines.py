from typing import Any

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr, synonym

Base = declarative_base()


class ToDictMixin:
    """
    Миксин для преобразования экземпляра модели SQLAlchemy в словарь.

    Методы:
        to_dict: Возвращает словарь, содержащий значения атрибутов объекта, за исключением служебных полей.

    Атрибуты:
        _exclude_params: Список имен атрибутов, которые должны быть исключены из результата (по умолчанию содержит `_sa_instance_state`).
    """

    _exclude_params = ["_sa_instance_state"]

    def to_dict(self) -> dict[str, Any]:

        data_dict = {
            k: v for k, v in self.__dict__.items() if k not in self._exclude_params
        }

        return data_dict


class PropertyAliasMixin:
    """Mixin создаёт псевдоним `day_property` на одно из существующих полей."""

    @declared_attr
    def day_property(cls):
        if hasattr(cls, "moon_day"):
            target_field = "moon_day"
        elif hasattr(cls, "name"):
            target_field = "name"
        elif hasattr(cls, "month"):
            target_field = "month"
        elif hasattr(cls, "en_name"):
            target_field = "en_name"
        else:
            raise AttributeError(
                f"{cls.__name__} должен содержать одно из полей: moon_day, month или en_name"
            )
        # создаём безопасный ORM-синоним без предупреждений
        return synonym(target_field)
