from typing import Any

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import ColumnProperty

Base = declarative_base()


class ToDictMixin:
    _exclude_params = ["id", "_sa_instance_state"]

    def to_dict(self) -> dict[str, Any]:

        data_dict = {
            k: v for k, v in self.__dict__.items() if k not in self._exclude_params
        }

        return data_dict
