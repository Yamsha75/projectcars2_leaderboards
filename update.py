from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import and_, func, or_

from db import get_session
from logger import logger
from models import LapRecord, Player, Subscription, Track, Vehicle
from scrape import scrape_lap_records
from settings import (
    HIGH_UPDATE_INTERVAL,
    LOW_UPDATE_INTERVAL,
    LOW_UPDATE_THRESHOLD,
    MID_UPDATE_INTERVAL,
)


def insert_records(
    subscription: Subscription, lap_records: pd.DataFrame
) -> (int, int):
    session = get_session()
    current_records_query = session.query(LapRecord).filter_by(
        subscription=subscription
    )
    added_rows_count = 0
    updated_rows_count = 0
    for record in lap_records.to_dict("records"):
        lr = current_records_query.filter_by(
            player_id=record["player_id"]
        ).first()
        if not lr:
            lr = LapRecord(
                subscription=subscription,
                track=subscription.track,
                vehicle=subscription.vehicle,
                **record,
            )
            session.add(lr)
            added_rows_count += 1
        else:
            lr.update(**record)
            updated_rows_count += 1
    session.flush()

    if not (added_rows_count or updated_rows_count):
        logger.info("No new or updated lap records")
    else:
        logger.info(
            f"Added {added_rows_count} and updated {updated_rows_count} lap records"
        )
    return added_rows_count, updated_rows_count


def update_interval(subscription: Subscription):
    session = get_session()

    has_tracked_player = (
        session.query(LapRecord)
        .join(Player)
        .filter(LapRecord.subscription == subscription)
        .first()
        is not None
    )
    if has_tracked_player:
        if subscription.update_interval_hours != HIGH_UPDATE_INTERVAL:
            logger.info(
                "Found new record by tracked player. Updating update_interval_hours"
            )
            subscription.update_interval_hours = HIGH_UPDATE_INTERVAL
    elif len(subscription.lap_records) > LOW_UPDATE_THRESHOLD:
        if subscription.update_interval_hours != MID_UPDATE_INTERVAL:
            subscription.update_interval_hours = MID_UPDATE_INTERVAL
    elif subscription.update_interval_hours != LOW_UPDATE_INTERVAL:
        subscription.update_interval_hours = LOW_UPDATE_INTERVAL
    session.commit()


def update_intervals():
    session = get_session()

    # set update_interval_hours to subscriptions with tracked players
    subscriptions_to_update = (
        session.query(Subscription)
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
        session.query(Subscription, func.count(Subscription.lap_records))
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

    session.commit()
    return True


def update_subscription(subscription: Subscription):
    lap_records = scrape_lap_records(
        subscription.track_id, subscription.vehicle_id
    )
    insert_records(subscription, lap_records)
    update_interval(subscription)
    subscription.last_update = datetime.utcnow()
    subscription.next_update = subscription.last_update + timedelta(
        hours=subscription.update_interval_hours
    )
    return True


def update_records(limit: int = -1):
    # -1 means no limit
    session = get_session()
    now = datetime.utcnow()
    subscriptions_to_update = (
        session.query(Subscription)
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
        update_subscription(s)
    session.commit()
    return True


if __name__ == "__main__":
    update_records(10)
