"""
https://gist.github.com/shambarick/51c955e55cf61a9e6e339f4c0223b938
"""

import logging
import os
import sys

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

CUSTOM_LOGURU_FORMAT = "{extra[trace_id]:<30} | " + LOGURU_FORMAT
IS_DEBUG_ENABLED = os.environ.get("IS_DEBUG_ENABLED", True)
IS_LOCAL_DEV = os.environ.get("LOCAL_DEV", False)


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
            # AWS CloudWatch does not support ANSI color codes
            {
                "sink": sys.stdout,
                "level": logging.DEBUG if IS_DEBUG_ENABLED else logging.INFO,
                "format": CUSTOM_LOGURU_FORMAT,
                "colorize": IS_LOCAL_DEV,
                "backtrace": False,
            },
        ],
        extra={"trace_id": ""},
    )
