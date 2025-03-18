import logging
from logging.handlers import RotatingFileHandler

from core import settings


def init_logger():
    log_level = settings.logger.log_level
    log_file = settings.logger.filename
    numeric_level = getattr(logging, log_level.upper(), logging.ERROR)
    handler = RotatingFileHandler(
        log_file, maxBytes=1 * 1024 * 1024, backupCount=1  # 5 MB, 3 backup files
    )
    logging.basicConfig(
        filename=log_file,
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
