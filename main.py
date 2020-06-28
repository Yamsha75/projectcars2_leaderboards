import db
from events import new_tracked_player_event
from models import LapRecord, Player, Subscription
from settings import HIGH_UPDATE_INTERVAL
from update import update_records


def add_player(steam_id: str, name: str, update_intervals: bool = True):
    player = Player(steam_id=steam_id, name=name)
    db.session.add(player)
    db.session.commit()

    new_tracked_player_event.publish(player=player)

    if update_intervals:
        for record in player.lap_records:
            s = record.subscription
            if s.update_interval_hours != HIGH_UPDATE_INTERVAL:
                s.update_interval_hours = HIGH_UPDATE_INTERVAL
        db.session.commit()
    return True


if __name__ == "__main__":
    update_records(100)
