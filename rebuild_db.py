from db import get_base, get_engine, get_session
from models import Track, TrackedPair, Vehicle, VehicleClass
from static_data_api import get_tracks, get_vehicle_classes, get_vehicles


def rebuild_db():
    print("Recreating tables... ", end="")
    get_base().metadata.create_all(bind=get_engine())
    print("Done")

    print("Populating tables... ")
    session = get_session()
    table_data_getters = {
        Track: get_tracks,
        VehicleClass: get_vehicle_classes,
        Vehicle: get_vehicles,
    }

    for _class, getter in table_data_getters.items():
        print(f"- Populating table '{_class.__tablename__}'... ", end="")
        items = getter().to_dict("records")
        print(f"Adding {len(items)} items... ", end="")
        for item in items:
            Item = _class(**item)
            session.merge(Item)
        session.commit()
        print("OK")

    print(f"- Populating table '{TrackedPair.__tablename__}'... ", end="")
    tracks = get_tracks()["id"]
    vehicles = get_vehicles()["id"]
    print(f"Adding {len(tracks) * len(vehicles)} items...", end="")
    for _, track in tracks.iteritems():
        for _, vehicle in vehicles.iteritems():
            t_pair = TrackedPair(track_id=track, vehicle_id=vehicle)
            session.merge(t_pair)
        session.commit()
    print("OK")

    session.close()
    print("Done")
    return True


if __name__ == "__main__":
    rebuild_db()
