import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from logger import logger
from settings import DATASOURCE_URL


def parse_time(df: pd.Series) -> pd.Series:
    # parts = (minutes, seconds, milliseconds)
    parts = df.str.extract(r"(\d{0,2}):(\d{2})\.(\d{3})").astype(int)
    return (parts[0] * 60 + parts[1]) * 1000 + parts[2]


def prepare_soup(track_id: int, vehicle_id: int, page: int = 1):
    # request and cook the soup
    url = DATASOURCE_URL.format(
        track_id=track_id, vehicle_id=vehicle_id, page=page
    )
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def scrape_lap_records(
    track_id: int, vehicle_id: int, pages_limit: int = 0
) -> pd.DataFrame:

    soup = prepare_soup(track_id, vehicle_id)

    if soup.find("p", class_="error"):
        logger.error(
            f"track_id={track_id} and/or vehicle_id={vehicle_id} is invalid!"
        )
        raise ValueError("invalid track_id and/or vehicle_id")

    if soup.find("tr", class_="no_data"):
        # no records found
        logger.info(
            f"Found 0 records for vehicle {vehicle_id} on track {track_id}"
        )
        return pd.DataFrame()

    if pages_limit == 1:
        # only the first page; no need to check how many pages are available
        pass
    else:
        # check number of pages (max 100 records per page)
        page_marker = soup.find("select", id="pager_top_select_page")
        if page_marker:
            # more than 1 page available
            max_pages = int(page_marker.find_all("option")[-1].text)
            if pages_limit == 0:
                # all pages
                pages_limit = max_pages
            else:
                pages_limit = min(max_pages, pages_limit)
        else:
            # only 1 page available
            pages_limit = 1

    logger.info(
        f"Found {pages_limit} page(s) of times for vehicle {vehicle_id} on track {track_id}"
    )

    # temp list for lap times tuples
    lap_times = []
    for page in range(1, pages_limit + 1):
        if page == 1:
            pass  # page 1 is already requested
        else:
            soup = prepare_soup(track_id, vehicle_id, page)

        rows = (
            soup.find("table", class_="leaderboard")
            .find_all("tbody")[-1]
            .find_all("tr")
        )
        for row in rows:
            user_td = row.find("td", class_="user")
            username = user_td.text[1:-1]
            if username != "<unknown>":
                steam_id = user_td["id"][5:]
                sectors = re.findall(
                    r"Sector \d: (\d+:\d+\.\d+)",
                    row.find("td", class_="time")["title"],
                )
                if sectors and len(sectors) == 3:
                    time = row.find("span", class_="time").text
                    upload_date = row.find("td", class_="timestamp").text
                    lap_times.append(
                        (steam_id, username, time, *sectors, upload_date)
                    )

    # create dataframe from lap_times, adding column names
    df = pd.DataFrame(
        lap_times,
        columns=[
            "player_id",
            "player_name",
            "lap_time",
            "sector1",
            "sector2",
            "sector3",
            "upload_date",
        ],
    )

    # convert durations (str) to total millis (int)
    columns = ["lap_time", "sector1", "sector2", "sector3"]
    for column_name in columns:
        df[column_name] = parse_time(df[column_name])

    # convert timestamp (str) to datetime.datetime
    df["upload_date"] = pd.to_datetime(df["upload_date"], dayfirst=True)

    return df
