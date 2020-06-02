from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
                        Numeric, String)
from sqlalchemy.orm import relationship

from dtime import LapTime
from orm_base import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    length_km = Column(Numeric(precision=4, scale=2))

    def __init__(self, id, name, length_km):
        self.id = id
        self.name = name
        self.length_km = length_km

    def __str__(self):
        return self.name


class VehicleClass(Base):
    __tablename__ = "vehicle_classes"

    name = Column(String, primary_key=True)

    vehicles = relationship("Vehicle", back_populates="vehicle_class")

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vehicle_class_name = Column(
        String, ForeignKey("vehicle_classes.name"), nullable=False
    )
    year = Column(Integer, nullable=True)
    unique_in_class = Column(Boolean, default=False)

    vehicle_class = relationship("VehicleClass", back_populates="vehicles")

    def __init__(self, id, name, class_name, year, unique_in_class):
        self.id = id
        self.name = name
        # self.class_name = class_name
        self.vehicle_class = VehicleClass(class_name)
        self.year = year
        self.unique_in_class = unique_in_class

    def __str__(self):
        return self.name


class TrackedPlayer(Base):
    __tablename__ = "tracked_players"

    steam_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    lap_records = relationship("LapRecord")

    def __init__(self, steam_id, name):
        self.steam_id = steam_id
        self.name = name

    def __str__(self):
        return self.name


class TrackedPair(Base):
    __tablename__ = "tracked_pair"

    track_id = Column(Integer, ForeignKey("tracks.id"), primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), primary_key=True)
    last_update = Column(DateTime)

    track = relationship("Track")
    vehicle = relationship("Vehicle")


class LapRecord(Base):
    __tablename__ = "lap_records"

    track_id = Column(Integer, ForeignKey("tracks.id"), primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), primary_key=True)
    player_id = Column(String, ForeignKey("tracked_players.steam_id"), primary_key=True)
    player_name = Column(String, nullable=True)
    lap_time = Column(Integer, nullable=False)
    sector1 = Column(Integer)
    sector2 = Column(Integer)
    sector3 = Column(Integer)
    upload_date = Column(DateTime)

    track = relationship("Track")
    vehicle = relationship("Vehicle")
    player = relationship("TrackedPlayer", back_populates="lap_records")

    def __init__(
        self,
        track_id,
        vehicle_id,
        player_id,
        player_name,
        lap_time,
        sector1,
        sector2,
        sector3,
        upload_date,
    ):
        self.track_id = track_id
        self.vehicle_id = vehicle_id
        self.player_id = player_id
        self.player_name = player_name
        self.lap_time = lap_time
        self.sector1 = sector1
        self.sector2 = sector2
        self.sector3 = sector3
        self.upload_date = upload_date

    def __str__(self):
        lap_time = LapTime(milliseconds=self.lap_time)
        if self.player:
            return f"Lap record: {lap_time} using {self.vehicle} on {self.track} by {self.player}"
        else:
            return f"Lap record: {lap_time} using {self.vehicle} on {self.track} by {self.player_name}"
