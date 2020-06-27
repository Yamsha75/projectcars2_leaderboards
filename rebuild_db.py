from db import get_base, get_engine, get_session
from logger import logger
from models import Track, Subscription, Vehicle
from settings import MID_UPDATE_INTERVAL
from static_data_api import get_tracks, get_vehicles


def rebuild_db():
    logger.info("Started recreating tables")
    get_base().metadata.create_all(bind=get_engine())
    logger.info("Finished recreating tables")

    logger.info("Started populating tables")
    session = get_session()

    logger.info("Started populating table 'tracks'")
    tracks = get_tracks()
    logger.info(f"Adding {len(tracks)} rows to table 'tracks'")
    for _, t in tracks.iterrows():
        T = Track(id=t["id"], name=t["name"], length_km=t["length_km"])
        session.merge(T)
    session.commit()
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
        session.merge(V)
    session.commit()
    logger.info("Finished populating table 'vehicles'")

    logger.info("Started populating table 'subscriptions'")
    logger.info(
        f"Adding {len(tracks) * len(vehicles)} rows to table 'subscriptions'"
    )
    for _, track in tracks.iterrows():
        for _, vehicle in vehicles.iterrows():
            if (
                not session.query(Subscription)
                .filter_by(track_id=track["id"], vehicle_id=vehicle["id"])
                .first()
            ):
                S = Subscription(track_id=track["id"], vehicle_id=vehicle["id"])
                if not (track["ignored"] or vehicle["ignored"]):
                    S.update_interval_hours = MID_UPDATE_INTERVAL
                session.merge(S)
        session.commit()
    logger.info("Finished populating table 'subscriptions'")

    session.close()
    logger.info("Finished populating tables")
    return True


if __name__ == "__main__":
    rebuild_db()
