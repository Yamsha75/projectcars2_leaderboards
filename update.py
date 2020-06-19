from datetime import datetime, timedelta

from sqlalchemy import or_

from db import get_session
from logger import logger
from models import TrackedPair
from scrape import scrape_times
from settings import (
    HIGH_UPDATE_INTERVAL,
    LOW_UPDATE_INTERVAL,
    LOW_UPDATE_THRESHOLD,
    MID_UPDATE_INTERVAL,
)


def update_records(limit: int = -1):
    # -1 means no limit
    session = get_session()
    now = datetime.utcnow()
    tracked_pairs = (
        session.query(TrackedPair)
        .filter(TrackedPair.update_interval_hours != None)
        .filter(or_(TrackedPair.last_update == None, TrackedPair.next_update <= now))
        .order_by(TrackedPair.next_update)
        .limit(limit)
    )
    for tp in tracked_pairs:
        n, found_tracked_player = scrape_times(tp.track_id, tp.vehicle_id)
        if found_tracked_player:
            if tp.update_interval_hours != HIGH_UPDATE_INTERVAL:
                tp.update_interval_hours = HIGH_UPDATE_INTERVAL
                logger.info("Found new record by tracked player")
        elif n < LOW_UPDATE_THRESHOLD:
            if tp.update_interval_hours != LOW_UPDATE_INTERVAL:
                tp.update_interval_hours = LOW_UPDATE_INTERVAL
        else:
            if tp.update_interval_hours != MID_UPDATE_INTERVAL:
                tp.update_interval_hours = MID_UPDATE_INTERVAL
        tp.last_update = datetime.utcnow()
        tp.next_update = tp.last_update + timedelta(
            hours=tp.update_interval_hours
        )
        session.commit()
    session.close()
