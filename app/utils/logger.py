"""
Mainly from:
    https://gist.github.com/shambarick/51c955e55cf61a9e6e339f4c0223b938
"""

import logging
import os
from pathlib import Path
import sys

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from models.environment import Environment

CUSTOM_LOGURU_FORMAT = "{extra[trace_id]:<30} | " + LOGURU_FORMAT
LOGGING_LEVEL = "DEBUG" if os.environ.get("ENV") != Environment.PROD else "INFO"

LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru document.
    See https://loguru.readthedocs.io/en/stable/overview.html#\
        entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger():
    # disable handlers for specific uvicorn loggers
    # to redirect their output to the default uvicorn logger
    # works with uvicorn==0.11.6
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    # change handler for default uvicorn logger
    intercept_handler = InterceptHandler()
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    logging.getLogger("sqlalchemy.engine.Engine").handlers = [intercept_handler]
    # set logs output, level and format
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": LOGGING_LEVEL,
                "format": CUSTOM_LOGURU_FORMAT,
            },
        ],
        extra={"trace_id": ""},
    )

    logger.add(
        LOG_PATH / "fasm_{time:YYYY-MM-DD}.log",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        level=LOGGING_LEVEL,
        format=CUSTOM_LOGURU_FORMAT,
        enqueue=True,
    )

    logger.debug("Logger setup completed.")
