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

    subscriptions = relationship("Subscription")

    def __str__(self):
        return self.name

    _repr_fields = ["id", "name"]


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    class_ = Column("class", String, nullable=False)
    year = Column(Integer, nullable=True)
    unique_in_class = Column(Boolean, default=False)

    subscriptions = relationship("Subscription")

    def __str__(self):
        return self.name

    _repr_fields = ["id", "name", "class_"]


class Player(Base):
    __tablename__ = "players"

    steam_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    lap_records = relationship("LapRecord")

    def __str__(self):
        return self.name

    _repr_fields = ["steam_id", "name"]


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

    track = relationship("Track", back_populates="subscriptions")
    vehicle = relationship("Vehicle", back_populates="subscriptions")
    lap_records = relationship("LapRecord")

    def __str__(self):
        return f"Subscription: {self.vehicle} on {self.track}"

    _repr_fields = ["id", "track", "vehicle"]


class LapRecord(Base):
    __tablename__ = "lap_records"

    subscription_id = Column(
        Integer, ForeignKey("subscriptions.id"), primary_key=True
    )
    player_id = Column(String, ForeignKey("players.steam_id"), primary_key=True)
    player_name = Column(String, nullable=False)
    lap_time = Column(Integer, nullable=False)
    sector1 = Column(Integer)
    sector2 = Column(Integer)
    sector3 = Column(Integer)
    upload_date = Column(DateTime, nullable=False)

    subscription = relationship("Subscription", back_populates="lap_records")
    player = relationship("Player", back_populates="lap_records")

    _repr_fields = [
        "subscription",
        "player_id",
        "player_name",
        "lap_time",
        "upload_date",
    ]

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
            player_name = str(self.player)
        else:
            player_name = self.player_name
        return f"LapRecord of {formatted_time} using {self.subscription.vehicle} on {self.subscription.track} by {player_name}"
