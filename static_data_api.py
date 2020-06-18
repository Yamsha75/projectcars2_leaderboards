from csv import reader


DATA_PATH = "static_data/"


def import_csv(filename: str):
    rows = reader(open(DATA_PATH + filename, encoding="utf8"))
    headers = next(rows)
    return list(rows)


def get_tracks():
    return import_csv("tracks.csv")


def get_vehicles():
    return import_csv("vehicles.csv")
