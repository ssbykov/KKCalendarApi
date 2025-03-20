import logging
from pathlib import Path
from typing import Any, Optional

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType as _ImageType
from sqlalchemy.engine.interfaces import Dialect

try:
    from PIL import Image, UnidentifiedImageError

    PIL = True
except ImportError:  # pragma: no cover
    PIL = False

from fastapi_storages.base import StorageImage

from core import settings


class ImageType(_ImageType):  # type: ignore[misc]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            storage=FileSystemStorage(path=settings.image_storage.full_path),
            *args,
            **kwargs,
        )

    def process_result_value(
        self, value: Any, dialect: Dialect
    ) -> Optional[StorageImage]:
        if value is None:
            return value

        file_path = self.storage.get_path(value)
        if not Path(file_path).exists():
            logging.error(f"Файл {file_path} не найден.")
            return None

        try:
            with Image.open(file_path) as image:
                return StorageImage(
                    name=value,
                    storage=self.storage,
                    height=image.height,
                    width=image.width,
                )
        except UnidentifiedImageError:
            logging.error(f"Файл {file_path} не является изображением.")
            return None
        except Exception as e:
            logging.error(f"Ошибка при обработке изображения: {e}")
            return None
