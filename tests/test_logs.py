import logging

from i2psam.logs import LOG_NAME, configure_logging, get_logger


def test_get_logger_root_and_child_names():
    assert get_logger().name == LOG_NAME
    assert get_logger("client").name == f"{LOG_NAME}.client"


def test_configure_logging_is_idempotent_for_same_handler():
    logger = get_logger()
    prev_handlers = list(logger.handlers)

    handler = logging.StreamHandler()
    configured = configure_logging(logging.DEBUG, handler=handler)
    configure_logging(logging.INFO, handler=handler)

    assert configured is logger
    assert logger.level == logging.INFO
    assert logger.handlers.count(handler) == 1

    for h in logger.handlers[:]:
        logger.removeHandler(h)
    for h in prev_handlers:
        logger.addHandler(h)
