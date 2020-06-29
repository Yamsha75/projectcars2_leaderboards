import requests

from settings import STEAM_API_KEY


def get_steam_user_summary(steam_id: str):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["response"]["players"][0]


def get_steam_user_avatar_url(steam_id: str):
    public_data = get_steam_user_summary(steam_id)
    if public_data:
        return public_data["avatarfull"]
