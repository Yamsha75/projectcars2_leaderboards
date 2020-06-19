from os import getenv

from dotenv import load_dotenv

load_dotenv()

DEBUG = getenv("DEBUG").lower() == "true"

LOW_UPDATE_THRESHOLD = int(getenv("LOW_UPDATE_THRESHOLD"))

LOW_UPDATE_INTERVAL = int(getenv("LOW_UPDATE_INTERVAL"))
MID_UPDATE_INTERVAL = int(getenv("MID_UPDATE_INTERVAL"))
HIGH_UPDATE_INTERVAL = int(getenv("HIGH_UPDATE_INTERVAL"))

DB_CONNECT_STR = getenv("DB_CONNECT_STR")
DATASOURCE_URL = getenv("DATASOURCE_URL")

G_SHEETS_SHEET = getenv("G_SHEETS_SHEET")
G_SHEETS_SCOPE = getenv("G_SHEETS_SCOPE")
G_SHEETS_TOKEN = getenv("G_SHEETS_TOKEN")
