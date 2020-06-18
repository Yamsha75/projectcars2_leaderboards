from db import get_base, get_engine, get_session
from models import Track, TrackedPair, Vehicle
from static_data_api import get_tracks, get_vehicles

def printn(s: str):
    print(s, end="", flush=True)


def rebuild_db():
    printn("Recreating tables... ")
    get_base().metadata.create_all(bind=get_engine())
    print("Done")

    print("Populating tables... ")
    session = get_session()

    printn(f"- Populating table 'tracks'... ")
    tracks = get_tracks()
    printn(f"Adding {len(tracks)} rows... ")
    for t in tracks:
        length_km = float(t[2]) if t[2] else None
        T = Track(id=int(t[0]), name=t[1], length_km=length_km)
        session.merge(T)
    session.commit()
    print("OK")

    printn(f"- Populating table 'vehicles'... ")
    vehicles = get_vehicles()
    printn(f"Adding {len(vehicles)} rows... ")
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
    print("OK")

    printn(f"- Populating table 'tracked_pairs'... ")
    tracks = get_tracks()
    vehicles = get_vehicles()
    printn(f"Adding {len(tracks) * len(vehicles)} rows... ")
    for t in tracks:
        if t[3] == '0':
            for v in vehicles:
                if v[5] == '0':
                    TP = TrackedPair(track_id=int(t[0]), vehicle_id=int(v[0]))
                    session.merge(TP)
            session.commit()
    print("OK")

    session.close()
    print("Done")
    return True


if __name__ == "__main__":
    rebuild_db()
