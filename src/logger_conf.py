import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig

from colorlog import ColoredFormatter

from .settings import settings


def init_logger() -> logging.Logger:
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s (%(name)s:%(lineno)d)",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'green',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s (%(name)s:%(lineno)d)"
    )

    file_handler = RotatingFileHandler(
        settings.DATA_PATH+"/"+settings.LOG_FILE_NAME,
        encoding="utf-8",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.ERROR)

    logger = logging.getLogger("custom_logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
