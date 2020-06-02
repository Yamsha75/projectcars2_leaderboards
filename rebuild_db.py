from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker

from models import Track, Vehicle, VehicleClass
from orm_base import Base, create_new_session
from static_data_api import get_tracks, get_vehicle_classes, get_vehicles


def rebuild_db(db_engine: engine):
    session = create_new_session(db_engine)

    print("Recreating tables... ", end="")
    Base.metadata.create_all(db_engine)
    print("Done")

    print("Populating tables... ")
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

    session.end()
    print("Done")
    return True


if __name__ == "__main__":
    load_dotenv()
    connection_string = getenv("DB_CONNECTION_STRING")
    engine = create_engine(connection_string)
    rebuild_db(engine)
