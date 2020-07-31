from datetime import datetime, timedelta

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

import db
from events import improved_record_event, new_record_event
from logger import logger
from scrape import scrape_lap_records
from settings import (
    HIGH_UPDATE_INTERVAL,
    LOW_UPDATE_INTERVAL,
    LOW_UPDATE_THRESHOLD,
    MID_UPDATE_INTERVAL,
)


class Player(db.base):
    __tablename__ = "players"

    steam_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    lap_records = relationship("LapRecord")

    _repr_fields = ["steam_id", "name"]

    def __str__(self):
        return self.name


class Track(db.base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    length_km = Column(Float)
    ignored = Column(Boolean)

    subscriptions = relationship("Subscription")

    _repr_fields = ["id", "name"]

    def __str__(self):
        return self.name


class VehicleClass(db.base):
    __tablename__ = "vehicle_classes"

    id = Column(String(4), primary_key=True)
    name = Column(String, nullable=False)
    ignored = Column(Boolean)

    vehicles = relationship("Vehicle")

    _repr_fields = ["id", "name"]

    def __str__(self):
        return self.name


class Vehicle(db.base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    class_id = Column(String, ForeignKey("vehicle_classes.id"))
    ignored = Column(Boolean)

    class_ = relationship("VehicleClass", back_populates="vehicles")
    subscriptions = relationship("Subscription")

    _repr_fields = ["id", "name", "class_"]

    def __str__(self):
        return self.name


class VehicleDetails(db.base):
    __tablename__ = "vehicle_details"

    id = Column(Integer, ForeignKey("vehicles.id"), primary_key=True)
    year = Column(Integer)
    drivetrain = Column(String(3))
    top_speed_kmph = Column(Integer)
    accel_to_100kmph = Column(Float)
    bhp = Column(Integer)
    mass_kg = Column(Integer)
    gears = Column(Integer)
    engine = Column(String(3))
    abs = Column(Boolean)
    tc = Column(Boolean)
    sc = Column(Boolean)
    control_difficulty = Column(Integer)
    cornering_speed = Column(Integer)

    vehicle = relationship("Vehicle", uselist=False, backref="details")

    _repr_fields = [
        "year",
        "drivetrain",
        "top_speed_kmph",
        "accel_to_100kmph",
        "bhp",
        "mass_kg",
        "gears",
        "engine",
        "abs",
        "tc",
        "sc",
        "control_difficulty",
        "cornering_speed",
    ]

    def __str__(self):
        return f"VehicleDetails of {self.vehicle}"


class Subscription(db.base):
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

    _repr_fields = ["id", "track", "vehicle"]

    def __str__(self):
        return f"Subscription: {self.vehicle} on {self.track}"

    def update(self, lap_records: List[LapRecordTuple], forced=False):
        current_records = {
            lap_record.player_id: lap_record for lap_record in self.lap_records
        }
        for record in lap_records:
            old_record = current_records.get(record.player_id)
            if not old_record:
                # new lap record
                lr = LapRecord(subscription=self, **record._asdict())
                db.session.add(lr)
            elif old_record.lap_time > record.lap_time:
                old_record.update(**record)
        db.session.commit()
        # refresh update_interval
        tracked_player = (
            db.session.query(LapRecord)
            .join(Player)
            .filter(LapRecord.subscription == self)
            .first()
        )
        if tracked_player:
            if self.update_interval_hours != HIGH_UPDATE_INTERVAL:
                logger.info(
                    "Found new record by tracked player. Updating update_interval_hours"
                )
                self.update_interval_hours = HIGH_UPDATE_INTERVAL
        elif len(self.lap_records) > LOW_UPDATE_THRESHOLD:
            if self.update_interval_hours != MID_UPDATE_INTERVAL:
                self.update_interval_hours = MID_UPDATE_INTERVAL
        elif self.update_interval_hours != LOW_UPDATE_INTERVAL:
            self.update_interval_hours = LOW_UPDATE_INTERVAL
        db.session.commit()
        # refresh last_update and next_update
        self.last_update = datetime.utcnow()
        self.next_update = self.last_update + timedelta(
            hours=self.update_interval_hours
        )
        db.session.commit()


class LapRecord(db.base):
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
    controller_id = Column(String, ForeignKey("controllers.id"), nullable=True)
    upload_date = Column(DateTime, nullable=False)

    subscription = relationship("Subscription", back_populates="lap_records")
    player = relationship("Player", back_populates="lap_records")
    controller = relationship("Controller", back_populates="lap_records")

    _repr_fields = [
        "subscription",
        "player_id",
        "player_name",
        "lap_time",
        "controller",
        "upload_date",
    ]

    def __str__(self):
        formatted_time = self.format_time(self.lap_time)
        if self.player:
            player_name = str(self.player)
        else:
            player_name = self.player_name
        return f"LapRecord of {formatted_time} using {self.subscription.vehicle} on {self.subscription.track} by {player_name}"

    def update(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)

    @staticmethod
    def format_time(millis: int) -> str:
        seconds, millis = divmod(millis, 1000)
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}.{millis:03d}"


class Controller(db.base):
    __tablename__ = "controllers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    lap_records = relationship("LapRecord")

    _repr_fields = ["id", "name"]

    def __str__(self):
        return self.name
