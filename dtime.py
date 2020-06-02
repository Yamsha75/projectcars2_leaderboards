from datetime import timedelta

class LapTime(timedelta):
    def __str__(self):
        minutes, seconds = divmod(self.seconds, 60)
        millis = self.microseconds // 1000
        return f"{minutes:02d}:{seconds:02d}.{millis:03d}"
