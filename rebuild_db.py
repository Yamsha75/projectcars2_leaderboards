import pandas as pd

import db
from logger import logger
from models import (
    Controller,
    Subscription,
    Track,
    Vehicle,
    VehicleClass,
    VehicleDetails,
)
from settings import MID_UPDATE_INTERVAL
from static_data_api import (
    get_controllers,
    get_tracks,
    get_vehicle_classes,
    get_vehicle_details,
    get_vehicles,
)
from sqlalchemy import and_


def recreate_tables():
    logger.info("Started recreating tables")
    db.base.metadata.create_all(bind=db.engine)
    logger.info("Finished recreating tables")


def populate_table(class_: object, items: pd.DataFrame):
    table_name = class_.__tablename__
    # logger.info(f"Started populating table '{table_name}'")
    logger.info(f"Adding {items['id'].count()} rows to table '{table_name}'")
    for _, item in items.iterrows():
        I = class_(**item)
        db.session.merge(I)
    db.session.commit()
    logger.info(f"Finished populating table '{table_name}'")


def populate_tables():
    logger.info("Started populating tables")

    tracks = get_tracks()
    vehicle_classes = get_vehicle_classes()
    vehicles = get_vehicles()

    populate_table(Track, tracks)
    populate_table(VehicleClass, vehicle_classes)
    populate_table(Vehicle, vehicles)
    populate_table(VehicleDetails, get_vehicle_details())
    populate_table(Controller, get_controllers())

    logger.info(
        f"Adding {len(tracks) * len(vehicles)} rows to table 'subscriptions'"
    )
    ignored_classes = list(vehicle_classes[vehicle_classes["ignored"] == True]["id"])
    for _, track in tracks.iterrows():
        for _, vehicle in vehicles.iterrows():
            S = Subscription(track_id=track["id"], vehicle_id=vehicle["id"])
            if not (
                track["ignored"]
                or vehicle["ignored"]
                or vehicle["class_id"] in ignored_classes
            ):
                S.update_interval_hours = MID_UPDATE_INTERVAL
            db.session.merge(S)
        db.session.commit()
    logger.info(f"Finished populating table 'subscriptions'")

    logger.info("Finished populating tables")
    return True


if __name__ == "__main__":
    recreate_tables()
    populate_tables()
