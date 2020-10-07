import logging
from sys import stderr, stdout

from settings import DEBUG

file_logging_formatter = logging.Formatter(
    "%(asctime)s.%(msecs)03d [%(levelname)s] %(funcName)s@%(module)s: %(message)s",
    datefmt=r"%Y-%m-%d %H:%M:%S",
)
terminal_logging_formatter = logging.Formatter("[%(levelname)s] %(message)s")


class MaxLevelFilter(logging.Filter):
    def __init__(self, level):
        self.__level__ = level
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.__level__


def configure_handler(
    handler: logging.Handler,
    level: int,
    formatter: logging.Formatter,
    filter_: logging.Filter = None,
):
    handler.setLevel(level)
    handler.setFormatter(formatter)
    if filter_:
        handler.addFilter(filter_)
    return handler


file_handler = configure_handler(
    logging.FileHandler("app.log", encoding="utf-8"),
    logging.DEBUG,
    file_logging_formatter,
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

logger = logging.getLogger("pc2_leaderboards_logger")

logger.setLevel(logging.DEBUG)
for h in handlers:
    logger.addHandler(h)

if __name__ == "__main__":
    logger.debug("This is a debug print")
