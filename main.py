import db
from events import new_tracked_player_event
from models import LapRecord, Player, Subscription
from settings import HIGH_UPDATE_INTERVAL
from update import update_records


def add_player(steam_id: str, name: str, update_intervals: bool = True):
    p = Player(steam_id=steam_id, name=name)
    db.session.merge(p)
    db.session.commit()

    new_tracked_player_event.publish(player=p)

    if update_intervals:
        subscriptions_to_update = (
            db.session.query(Subscription)
            .join(LapRecord)
            .filter(LapRecord.player_id == steam_id)
            .filter(Subscription.update_interval_hours != HIGH_UPDATE_INTERVAL)
            .all()
        )
        for s in subscriptions_to_update:
            s.update_interval_hours = HIGH_UPDATE_INTERVAL

        db.session.commit()
    return True


if __name__ == "__main__":
    update_records(100)
