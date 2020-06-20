from db import get_session
from models import LapRecord, TrackedPair, TrackedPlayer
from update import update_records
from settings import HIGH_UPDATE_INTERVAL


def add_tracked_player(steam_id: str, name: str, update_intervals: bool = True):
    session = get_session()
    p = TrackedPlayer(steam_id=steam_id, name=name)
    session.merge(p)
    session.commit()

    if update_intervals:
        players_lap_records = session.query(LapRecord).filter_by(player=p).all()
        for r in players_lap_records:
            tp = session.query(TrackedPair).filter_by(
                track_id=r.track_id, vehicle_id=r.vehicle_id
            )
            if tp.update_interval_hours != HIGH_UPDATE_INTERVAL:
                tp.update_interval_hours = HIGH_UPDATE_INTERVAL
                session.commit()

    session.close()
    return True


if __name__ == "__main__":
    update_records(100)
