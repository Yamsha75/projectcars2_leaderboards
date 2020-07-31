import re
from datetime import datetime


def parse_datetime(s: str) -> datetime:
    """
    Parses datetime from string

    Parameters:
    s (str): datetime string with formatting: <dd/mm/YY HH:MM>

    Returns:
    datetime: parsed datetime
    """
    DATETIME_FORMAT = r"%d/%m/%Y %H:%M"

    return datetime.strptime(s, DATETIME_FORMAT)


def parse_lap_time(s: str) -> int:
    """
    Parses lap time in milliseconds from string
    
    Parameters:
    s (str): lap time string with formatting: <MM:SS.mmm>

    Returns:
    int: total milliseconds of lap time
    """
    LAP_TIME_PATTERN = r"(\d+):(\d{2})\.(\d{3})"

    matches = re.fullmatch(LAP_TIME_PATTERN, s).groups()
    minutes, seconds, millis = tuple(map(int, matches))
    return (minutes * 60 + seconds) * 1000 + millis
