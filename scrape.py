import asyncio
import re
from collections import namedtuple
from datetime import datetime
from typing import List

import aiohttp
import bs4

from logger import logger
from settings import DATASOURCE_URL
from time_parse import parse_datetime, parse_lap_time
from utils import flatten_list

SECTORS_PATTERN = r"Sector \d: (\d+:\d{2}\.\d{3})"

LapRecordTuple = namedtuple(
    "LapRecordTuple",
    [
        "player_id",
        "player_name",
        "lap_time",
        "sector1",
        "sector2",
        "sector3",
        "controller_id",
        "upload_date",
    ],
)

request_id = 0


async def _prepare_soup(
    http_session, track_id: int, vehicle_id: int, page: int = 1,
) -> bs4.BeautifulSoup:
    """
    Request records page and prepare BeautifulSoup
    """
    url = DATASOURCE_URL.format(
        track_id=track_id, vehicle_id=vehicle_id, page=page
    )
    global request_id
    request_id += 1
    id_ = request_id
    logger.debug(f"SENT request {id_}")
    response = await http_session.get(url)
    content = await response.text()
    logger.debug(f"RCVD request {id_}")
    soup = bs4.BeautifulSoup(content, "html.parser")
    return soup


def _get_rows_from_soup(soup: bs4.BeautifulSoup) -> List[bs4.element.Tag]:
    """
    Returns list of table rows from soup
    """
    return (
        soup.find("table", id="leaderboard")
        .find_all("tbody")[-1]
        .find_all("tr")
    )


async def _request_and_scrape_soup(
    http_session, track_id: int, vehicle_id: int, page: int = 1
) -> List[LapRecordTuple]:
    soup = await _prepare_soup(http_session, track_id, vehicle_id, page)
    lap_records = await _scrape_soup(soup)
    return lap_records


async def _scrape_soup(soup: bs4.BeautifulSoup) -> List[LapRecordTuple]:
    lap_records = []
    rows = _get_rows_from_soup(soup)
    for row in rows:
        user_td = row.find("td", class_="user")
        username = user_td.get_text(strip=True)
        if not username or username == "<unknown>":
            continue
        time_td = row.find("td", class_="time")
        sectors = tuple(
            map(parse_lap_time, re.findall(SECTORS_PATTERN, time_td["title"]))
        )
        if not sectors or len(sectors) != 3:
            continue
        lap_time = parse_lap_time(
            time_td.find("span", class_="time").get_text()
        )
        steam_id = user_td["id"][5:]
        assists_td = row.find("td", class_="assists")
        controller = assists_td.find_all("img")[1]["title"][12]
        upload_date = parse_datetime(
            row.find("td", class_="timestamp").get_text()
        )
        lap_records.append(
            LapRecordTuple(
                steam_id, username, lap_time, *sectors, controller, upload_date
            )
        )
    return lap_records


def _get_number_of_pages(soup: bs4.BeautifulSoup) -> int:
    if soup.find("tr", class_="no_data"):
        return 0
    page_select = soup.find("select", id="pager_top_select_page")
    if not page_select:
        return 1
    return int(page_select.find_all("option")[-1].get_text())


async def scrape_lap_records(
    http_session: aiohttp.ClientSession, track_id: int, vehicle_id: int
) -> List[LapRecordTuple]:
    first_soup = await _prepare_soup(http_session, track_id, vehicle_id)
    if first_soup.find("p", class_="error"):
        raise ValueError("invalid track_id and vehicle_id combination")

    number_of_pages = _get_number_of_pages(first_soup)
    if number_of_pages == 0:
        logger.debug()
        return []

    tasks = []
    for page_n in range(2, number_of_pages + 1):
        tasks.append(
            _request_and_scrape_soup(http_session, track_id, vehicle_id, page_n)
        )
    tasks.append(_scrape_soup(first_soup))

    results = flatten_list(await asyncio.gather(*tasks))
    logger.debug(
        f"Found {len(results)} records for track={track_id} and vehicle={vehicle_id}"
    )
    return results


if __name__ == "__main__":
    from pprint import pprint

    async def test_func(track_id, vehicle_id):
        async with aiohttp.ClientSession(raise_for_status=True) as client:
            result = await scrape_lap_records(client, track_id, vehicle_id)
        pprint(result[:5])

    asyncio.run(test_func(track_id=3878349996, vehicle_id=1934199723))
