import logging
from typing import Final


LOG_NAME: Final[str] = "i2psam"
_DEFAULT_FORMAT: Final[str] = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a package logger (or child logger)."""
    logger_name = LOG_NAME if not name else f"{LOG_NAME}.{name}"
    return logging.getLogger(logger_name)


def configure_logging(
    level: int | str = logging.INFO,
    *,
    handler: logging.Handler | None = None,
    fmt: str = _DEFAULT_FORMAT,
) -> logging.Logger:
    """
    Configure package logging.

    This function is idempotent and avoids adding duplicate handlers.
    """
    logger = get_logger()
    logger.setLevel(level)
    logger.propagate = False

    if handler is None:
        handler = logging.StreamHandler()

    if handler.formatter is None:
        handler.setFormatter(logging.Formatter(fmt))

    if handler not in logger.handlers:
        logger.addHandler(handler)

    return logger


get_logger().addHandler(logging.NullHandler())
