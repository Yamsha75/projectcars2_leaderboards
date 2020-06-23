import pandas as pd


def get_tracks() -> pd.DataFrame:
    return pd.read_csv("static_data/tracks.csv", dtype={"ignored": bool})


def get_vehicles() -> pd.DataFrame:
    return pd.read_csv(
        "static_data/vehicles.csv",
        dtype={"unique_in_class": bool, "ignored": bool},
    )


if __name__ == "__main__":
    print(get_tracks())
