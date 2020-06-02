import pandas as pd


def get_tracks() -> pd.DataFrame:
    return pd.read_csv("static_data/tracks.csv")


def get_vehicle_classes() -> pd.DataFrame:
    return pd.read_csv("static_data/vehicle_classes.csv")


def get_vehicles() -> pd.DataFrame:
    return pd.read_csv("static_data/vehicles.csv")
