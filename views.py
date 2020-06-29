from sqlalchemy import func

from db import session
from models import LapRecord, Player, Subscription, Track, Vehicle


def get_all_tracked_records():
    subquery = (
        session.query(
            Subscription.id.label("subscription_id"),
            func.min(LapRecord.lap_time).label("min_lap_time"),
        )
        .select_from(LapRecord)
        .join(Subscription)
        .group_by(Subscription.id)
        .subquery("subquery")
    )
    query = (
        session.query(
            LapRecord.upload_date,
            Player.name,
            Track.name,
            Vehicle.name,
            Vehicle.class_,
            LapRecord.lap_time,
            LapRecord.lap_time - subquery.c.min_lap_time,
        )
        .select_from(LapRecord)
        .join(Player, Subscription, Track, Vehicle)
        .filter(Subscription.id == subquery.c.subscription_id)
        .order_by(LapRecord.upload_date)
    )
    return query.all()


def get_top_tracked_per_track_and_class():
    subquery = (
        session.query(
            Track.id.label("track_id"),
            Vehicle.class_.label("vehicle_class"),
            func.min(LapRecord.lap_time).label("min_lap_time"),
        )
        .select_from(LapRecord)
        .join(Subscription, Track, Vehicle)
        .group_by(Track.id, Vehicle.class_)
        .subquery("subquery")
    )
    query = (
        session.query(
            Track.name,
            Vehicle.class_,
            Player.name,
            Vehicle.name,
            LapRecord.upload_date,
            LapRecord.lap_time,
            LapRecord.lap_time - subquery.c.min_lap_time,
        )
        .select_from(LapRecord)
        .join(Player, Subscription, Track, Vehicle)
        .filter(
            Track.id == subquery.c.track_id,
            Vehicle.class_ == subquery.c.vehicle_class,
        )
        .group_by(Track.id, Vehicle.class_)
    )
    return query.all()


if __name__ == "__main__":
    print(get_top_tracked_per_track_and_class())
