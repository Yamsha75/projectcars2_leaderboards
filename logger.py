import logging
from sys import stderr, stdout

from settings import DEBUG

datetime_format = r"%Y-%m-%d %H:%M:%S"
file_logging_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(module)s: %(message)s", datefmt=datetime_format
)
terminal_logging_formatter = logging.Formatter("[%(levelname)s] %(message)s")


class MaxLevelFilter(object):
    def __init__(self, level):
        self.__level__ = level

    def filter(self, logRecord: logging.LogRecord) -> bool:
        return logRecord.levelno <= self.__level__


file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_logging_formatter)

stderr_handler = logging.StreamHandler(stderr)
stderr_handler.setLevel(logging.WARNING)
stderr_handler.setFormatter(terminal_logging_formatter)

stdout_handler = logging.StreamHandler(stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(terminal_logging_formatter)
stdout_handler.addFilter(MaxLevelFilter(logging.INFO))


if DEBUG:
    handlers = [file_handler, stderr_handler, stdout_handler]
else:
    handlers = [file_handler, stderr_handler]

logging.basicConfig(level=logging.DEBUG, handlers=handlers)

logger = logging.getLogger()
