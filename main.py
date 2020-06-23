from db import get_session
from models import LapRecord, Player, Subscription
from settings import HIGH_UPDATE_INTERVAL
from update import update_records


def add_player(steam_id: str, name: str, update_intervals: bool = True):
    session = get_session()
    p = Player(steam_id=steam_id, name=name)
    session.merge(p)
    session.commit()

    if update_intervals:
        subscriptions_to_update = (
            session.query(Subscription)
            .join(LapRecord)
            .filter(LapRecord.player_id == steam_id)
            .filter(Subscription.update_interval_hours != HIGH_UPDATE_INTERVAL)
            .all()
        )
        for s in subscriptions_to_update:
            s.update_interval_hours = HIGH_UPDATE_INTERVAL

        session.commit()
    return True


if __name__ == "__main__":
    update_records(100)
