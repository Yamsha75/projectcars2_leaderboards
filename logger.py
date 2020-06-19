import logging
from sys import stderr, stdout

from settings import DEBUG

datetime_format = r"%Y-%m-%d %H:%M:%S"
file_logging_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(module)s: %(message)s", datefmt=datetime_format
)
terminal_logging_formatter = logging.Formatter("[%(levelname)s] %(message)s")


class MaxLevelFilter(logging.Filter):
    def __init__(self, level):
        self.__level__ = level

    def filter(self, logRecord: logging.LogRecord) -> bool:
        return logRecord.levelno <= self.__level__


def configure_handler(
    handler: logging.Handler,
    level: int,
    formatter: logging.Formatter,
    filter: logging.Filter = None,
):
    handler.setLevel(level)
    handler.setFormatter(formatter)
    if filter:
        handler.addFilter(filter)
    return handler


file_handler = configure_handler(
    logging.FileHandler("app.log"), logging.DEBUG, file_logging_formatter
)

stderr_handler = configure_handler(
    logging.StreamHandler(stderr), logging.WARNING, terminal_logging_formatter
)

handlers = [file_handler, stderr_handler]

if DEBUG:
    stdout_handler = configure_handler(
        logging.StreamHandler(stdout),
        logging.DEBUG,
        terminal_logging_formatter,
        MaxLevelFilter(logging.INFO),
    )
    handlers.append(stdout_handler)

logging.basicConfig(level=logging.DEBUG, handlers=handlers)

logger = logging.getLogger()


if __name__ == "__main__":
    logger.debug("This is a debug print")
