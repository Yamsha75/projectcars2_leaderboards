from db import get_base, get_engine, get_session
from logger import logger
from models import Track, TrackedPair, Vehicle
from settings import UPDATE_INTERVAL_HOURS
from static_data_api import get_tracks, get_vehicles


def rebuild_db():
    logger.info("Started recreating tables")
    get_base().metadata.create_all(bind=get_engine())
    logger.info("Finished recreating tables")

    logger.info("Started populating tables")
    session = get_session()

    logger.info("Started populating table 'tracks'")
    tracks = get_tracks()
    logger.info(f"Adding {len(tracks)} rows")
    for t in tracks:
        length_km = float(t[2]) if t[2] else None
        T = Track(id=int(t[0]), name=t[1], length_km=length_km)
        session.merge(T)
    session.commit()
    logger.info("Finished populating table 'tracks'")

    logger.info("Started populating table 'vehicles'")
    vehicles = get_vehicles()
    logger.info(f"Adding {len(vehicles)} rows")
    for v in vehicles:
        V = Vehicle(
            id=int(v[0]),
            name=v[1],
            vehicle_class_name=v[2],
            year=int(v[3]),
            unique_in_class=(v[4] == "1"),
        )
        session.merge(V)
    session.commit()
    logger.info("Finished populating table 'vehicles'")

    logger.info("Started populating table 'tracked_pairs'")
    tracks = get_tracks()
    vehicles = get_vehicles()
    logger.info(f"Adding {len(tracks) * len(vehicles)} rows")
    for track in tracks:
        ignored_track = track[3] == "1"
        for vehicle in vehicles:
            TP = TrackedPair(track_id=int(track[0]), vehicle_id=int(vehicle[0]))
            if not (ignored_track or vehicle[5] == "1"):
                TP.update_interval_hours = UPDATE_INTERVAL_HOURS
            session.merge(TP)
        session.commit()
    logger.info("Finished populating table 'tracked_pairs'")

    session.close()
    logger.info("Finished populating tables")
    return True


if __name__ == "__main__":
    rebuild_db()
