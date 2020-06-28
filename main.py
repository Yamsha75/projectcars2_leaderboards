from db import Session
from models import LapRecord, Player, Subscription, Track
from settings import HIGH_UPDATE_INTERVAL
from update import update_records


def add_player(steam_id: str, name: str, update_intervals: bool = True):
    p = Player(steam_id=steam_id, name=name)
    Session.merge(p)
    Session.commit()

    if update_intervals:
        subscriptions_to_update = (
            Session.query(Subscription)
            .join(LapRecord)
            .filter(LapRecord.player_id == steam_id)
            .filter(Subscription.update_interval_hours != HIGH_UPDATE_INTERVAL)
            .all()
        )
        for s in subscriptions_to_update:
            s.update_interval_hours = HIGH_UPDATE_INTERVAL

        Session.commit()
    return True


if __name__ == "__main__":
    update_records(100)
