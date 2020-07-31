import pandas as pd


def get_controllers() -> pd.DataFrame:
    return pd.read_csv("static_data/controllers.csv")


def get_tracks() -> pd.DataFrame:
    return pd.read_csv("static_data/tracks.csv")[["id", "name", "ignored"]]


def get_track_details() -> pd.DataFrame:
    return pd.read_csv("static_data/tracks.csv").drop(
        ["name", "ignored"], axis=1
    )


def get_vehicle_classes() -> pd.DataFrame:
    return pd.read_csv("static_data/vehicle_classes.csv")


def get_vehicles() -> pd.DataFrame:
    return pd.read_csv("static_data/vehicles.csv")[
        ["id", "name", "class_id", "ignored"]
    ]


def get_vehicle_details() -> pd.DataFrame:
    return pd.read_csv("static_data/vehicles.csv").drop(
        ["name", "class_id", "ignored"], axis=1
    )
