from datetime import timedelta

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from db import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    length_km = Column(Float, nullable=True)

    lap_records = relationship("LapRecord")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Track {self.__str__()}>"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    class_ = Column("class", String, nullable=False)
    year = Column(Integer, nullable=True)
    unique_in_class = Column(Boolean, default=False)

    lap_records = relationship("LapRecord")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Vehicle {self.__str__()}>"


class Player(Base):
    __tablename__ = "players"

    steam_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    lap_records = relationship("LapRecord")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Player {self.__str__()}>"


class Subscription(Base):
    __tablename__ = "subscriptions"
    __tableargs__ = tuple(
        UniqueConstraint("track_id", "vehicle_id", name="unique_track_vehicle")
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    update_interval_hours = Column(Integer, nullable=True)
    last_update = Column(DateTime, nullable=True)
    next_update = Column(DateTime, nullable=True)

    track = relationship("Track")
    vehicle = relationship("Vehicle")
    lap_records = relationship("LapRecord")

    def __str__(self):
        return f"Subscription: {self.vehicle} on {self.track}"

    def __repr__(self):
        return f"<{self.__str__()}>"


class LapRecord(Base):
    __tablename__ = "lap_records"

    subscription_id = Column(
        Integer, ForeignKey("subscriptions.id"), nullable=False
    )
    track_id = Column(Integer, ForeignKey("tracks.id"), primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), primary_key=True)
    player_id = Column(String, ForeignKey("players.steam_id"), primary_key=True)
    player_name = Column(String, nullable=True)
    lap_time = Column(Integer, nullable=False)
    sector1 = Column(Integer)
    sector2 = Column(Integer)
    sector3 = Column(Integer)
    upload_date = Column(DateTime)

    subscription = relationship("Subscription", back_populates="lap_records")
    track = relationship("Track", back_populates="lap_records")
    vehicle = relationship("Vehicle", back_populates="lap_records")
    player = relationship("Player", back_populates="lap_records")

    @staticmethod
    def format_time(millis: int):
        dt = timedelta(milliseconds=millis)
        minutes, seconds = divmod(dt.seconds, 60)
        millis = dt.microseconds // 1000
        return f"{minutes:02d}:{seconds:02d}.{millis:03d}"

    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def __str__(self):
        formatted_time = self.format_time(self.lap_time)
        if self.player:
            player = str(self.player)
        else:
            player = self.player_name
        return f"LapRecord {formatted_time} using {self.vehicle} on {self.track} by {player}"

    def __repr__(self):
        return f"<{self.__str__()}>"
