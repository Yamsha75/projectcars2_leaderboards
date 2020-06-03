from datetime import datetime

from db import get_session
from models import TrackedPair
from scrape import scrape_times


def update_tracked_pairs():
    session = get_session()
    t_pairs = session.query(TrackedPair).all()
    for t_pair in t_pairs:
        print(f"Updating lap times for {t_pair.vehicle} on {t_pair.track}...")
        track_id = t_pair.track_id
        vehicle_id = t_pair.vehicle_id
        scrape_times(track_id, vehicle_id)
        t_pair.last_update = datetime.utcnow()
        session.commit()
    return True


if __name__ == "__main__":
    update_tracked_pairs()
