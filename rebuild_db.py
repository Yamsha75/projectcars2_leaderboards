from db import Base, Engine, Session
from logger import logger
from models import Subscription, Track, Vehicle
from settings import MID_UPDATE_INTERVAL
from static_data_api import get_tracks, get_vehicles


def recreate_tables():
    logger.info("Started recreating tables")
    Base.metadata.create_all(bind=Engine)
    logger.info("Finished recreating tables")


def populate_tables():
    logger.info("Started populating tables")

    logger.info("Started populating table 'tracks'")
    tracks = get_tracks()
    logger.info(f"Adding {len(tracks)} rows to table 'tracks'")
    for _, t in tracks.iterrows():
        T = Track(id=t["id"], name=t["name"], length_km=t["length_km"])
        Session.merge(T)
    Session.commit()
    logger.info("Finished populating table 'tracks'")

    logger.info("Started populating table 'vehicles'")
    vehicles = get_vehicles()
    logger.info(f"Adding {len(vehicles)} rows to table 'vehicles'")
    for _, v in vehicles.iterrows():
        V = Vehicle(
            id=v["id"],
            name=v["name"],
            class_=v["class"],
            year=v["year"],
            unique_in_class=v["unique_in_class"],
        )
        Session.merge(V)
    Session.commit()
    logger.info("Finished populating table 'vehicles'")

    logger.info("Started populating table 'subscriptions'")
    logger.info(
        f"Adding {len(tracks) * len(vehicles)} rows to table 'subscriptions'"
    )
    for _, track in tracks.iterrows():
        for _, vehicle in vehicles.iterrows():
            if (
                not Session.query(Subscription)
                .filter_by(track_id=track["id"], vehicle_id=vehicle["id"])
                .first()
            ):
                S = Subscription(track_id=track["id"], vehicle_id=vehicle["id"])
                if not (track["ignored"] or vehicle["ignored"]):
                    S.update_interval_hours = MID_UPDATE_INTERVAL
                Session.merge(S)
        Session.commit()
    logger.info("Finished populating table 'subscriptions'")

    Session.close()
    logger.info("Finished populating tables")
    return True


if __name__ == "__main__":
    recreate_tables()
    populate_tables()
