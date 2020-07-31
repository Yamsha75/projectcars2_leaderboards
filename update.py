import asyncio
from datetime import datetime

import aiohttp
from sqlalchemy import func, or_

import db
from events import update_session_end_event, update_session_start_event
from models import LapRecord, Subscription
from scrape import scrape_lap_records
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


async def async_update_records(limit: int = -1, forced: bool = False):
    # limit == -1 means no limit
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
    async with aiohttp.ClientSession(raise_for_status=True) as client:
        tasks = [
            scrape_lap_records(client, s.track_id, s.vehicle_id)
            for s in subscriptions_to_update
        ]
        results = await asyncio.gather(*tasks)
    for s, lap_records in zip(subscriptions_to_update, results):
        s.update(lap_records, forced=forced)


def update_records(limit: int = -1, forced: bool = False):
    asyncio.run(async_update_records(limit, forced))


def update_high_interval_only(limit: int = -1, forced: bool = False):
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
        s.update(forced=forced)
    update_session_end_event.publish()
    return True


if __name__ == "__main__":
    update_records(2)
