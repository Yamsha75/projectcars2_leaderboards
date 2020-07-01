import pandas as pd


def get_controllers() -> pd.DataFrame:
    return pd.read_csv("static_data/controllers.csv")


def get_tracks() -> pd.DataFrame:
    return pd.read_csv("static_data/tracks.csv", dtype={"ignored": bool})


def get_vehicle_classes() -> pd.DataFrame:
    return pd.read_csv(
        "static_data/vehicle_classes.csv", dtype={"ignored": bool}
    )


def get_vehicle_details() -> pd.DataFrame:
    return pd.read_csv(
        "static_data/vehicle_details.csv",
        dtype={"abs": bool, "tc": bool, "sc": bool},
    )


def get_vehicles() -> pd.DataFrame:
    return pd.read_csv("static_data/vehicles.csv", dtype={"ignored": bool},)
