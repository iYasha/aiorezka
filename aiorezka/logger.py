import logging
from logging import config

import aiorezka

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(name)s] [%(levelname)s] %(asctime)s: %(message)s",
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {"": {"handlers": ["stdout"], "level": aiorezka.log_level}},
}


config.dictConfig(LOGGING)


def get_logger(name: str = aiorezka.default_logger_name) -> logging.Logger:
    return logging.getLogger(name)
