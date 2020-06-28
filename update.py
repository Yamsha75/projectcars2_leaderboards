from datetime import datetime

from sqlalchemy import func, or_

from db import Session
from models import LapRecord, Subscription
from settings import (
    HIGH_UPDATE_INTERVAL,
    LOW_UPDATE_INTERVAL,
    LOW_UPDATE_THRESHOLD,
    MID_UPDATE_INTERVAL,
)


def update_intervals():
    # set update_interval_hours to subscriptions with tracked players
    subscriptions_to_update = (
        Session.query(Subscription)
        .select_from(LapRecord)
        .join(Subscription)
        .filter(Subscription.update_interval_hours != None)
        .filter(Subscription.update_interval_hours != HIGH_UPDATE_INTERVAL)
        .filter(LapRecord.player.has())
        .all()
    )
    for s in subscriptions_to_update:
        s.update_interval_hours = HIGH_UPDATE_INTERVAL

    # check & set update_interval_hours to subscriptions without tracked players
    subscriptions_to_update = (
        Session.query(Subscription, func.count(Subscription.lap_records))
        .select_from(Subscription)
        .join(LapRecord)
        .all()
    )
    for s, lap_records_count in subscriptions_to_update:
        if lap_records_count < LOW_UPDATE_THRESHOLD:
            if s.update_interval_hours != LOW_UPDATE_INTERVAL:
                s.update_interval_hours = LOW_UPDATE_INTERVAL
        else:
            if s.update_interval_hours != MID_UPDATE_INTERVAL:
                s.update_interval_hours = MID_UPDATE_INTERVAL

    Session.commit()
    return True


def update_records(limit: int = -1):
    # -1 means no limit
    now = datetime.utcnow()
    subscriptions_to_update = (
        Session.query(Subscription)
        .filter(Subscription.update_interval_hours != None)
        .filter(
            or_(
                Subscription.last_update == None,
                Subscription.next_update <= now,
            )
        )
        .order_by(Subscription.next_update)
        .limit(limit)
    )
    for s in subscriptions_to_update:
        s.update()
    Session.commit()
    return True


if __name__ == "__main__":
    update_records(10)
