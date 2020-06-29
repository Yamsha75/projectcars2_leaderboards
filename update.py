from datetime import datetime

from sqlalchemy import func, or_

import db
from events import update_session_end_event, update_session_start_event
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
        db.session.query(Subscription)
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
        db.session.query(Subscription, func.count(Subscription.lap_records))
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

    db.session.commit()
    return True


def update_records(limit: int = -1):
    # -1 means no limit
    update_session_start_event.publish()
    now = datetime.utcnow()
    subscriptions_to_update = (
        db.session.query(Subscription)
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
    update_session_end_event.publish()
    return True


def update_high_interval_only(limit: int = -1):
    # -1 means no limit
    update_session_start_event.publish()
    now = datetime.utcnow()
    subscriptions_to_update = (
        db.session.query(Subscription)
        .filter_by(update_interval_hours=HIGH_UPDATE_INTERVAL)
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
    update_session_end_event.publish()
    return True


if __name__ == "__main__":
    update_records(10)
