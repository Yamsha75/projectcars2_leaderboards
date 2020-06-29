import requests

from events import (
    improved_record_event,
    new_record_event,
    new_tracked_player_event,
)
from models import LapRecord, Player
from settings import DISCORD_WEBHOOK
from steam_api import get_steam_user_avatar_url


def send_discord_message(payload):
    response = requests.post(DISCORD_WEBHOOK, json=payload)
    return response.status_code == 204


def format_discord_payload(title: str, description: str, steam_id: str = None):
    payload = {"title": title, "description": description}
    if steam_id:
        payload["thumbnail"] = {"url": get_steam_user_avatar_url(steam_id)}
    return {"embeds": [payload]}


def send_new_tracked_player_message(player: Player, found_records_count: int):
    message = f"Player {player.name} added to tracking list"
    if found_records_count:
        message += (
            f". Found {found_records_count} lap records already in database"
        )
    payload = format_discord_payload(
        title="New tracked player",
        description=message,
        steam_id=player.steam_id,
    )
    send_discord_message(payload)


new_tracked_player_event.add_observer(0, send_new_tracked_player_message)


def send_new_record_message(lap_record: LapRecord):
    formatted_time = LapRecord.format_time(lap_record.lap_time)
    message = f"""Found new record by {lap_record.player}!
    Time: {formatted_time}
    Track: {lap_record.subscription.track}
    Vehicle: {lap_record.subscription.vehicle}, class: {lap_record.subscription.vehicle.class_}
    """
    payload = format_discord_payload(
        title="New record found",
        description=message,
        steam_id=lap_record.player_id,
    )
    send_discord_message(payload)


new_record_event.add_observer(0, send_new_record_message)


def send_improved_record_message(lap_record: LapRecord, old_time: int):
    formatted_time = LapRecord.format_time(lap_record.lap_time)
    formatted_old_time = LapRecord.format_time(old_time)
    formatted_diff_time = LapRecord.format_time(old_time - lap_record.lap_time)
    message = f"""Found improved record by {lap_record.player}!
    New Time: {formatted_time}
    Old Time: {formatted_old_time} (-{formatted_diff_time})
    Track: {lap_record.subscription.track}
    Vehicle: {lap_record.subscription.vehicle}, class: {lap_record.subscription.vehicle.class_}
    """
    payload = format_discord_payload(
        title="Improved record found",
        description=message,
        steam_id=lap_record.player_id,
    )
    send_discord_message(payload)


improved_record_event.add_observer(0, send_improved_record_message)
