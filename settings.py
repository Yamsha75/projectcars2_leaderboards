from os import getenv

from dotenv import load_dotenv


load_dotenv()

DB_CONNECT_STR = getenv("DB_CONNECT_STR")
DATASOURCE_URL = getenv("DATASOURCE_ENV")

G_SHEETS_SHEET = getenv("G_SHEETS_SHEET")
G_SHEETS_SCOPE = getenv("G_SHEETS_SCOPE")
G_SHEETS_TOKEN = getenv("G_SHEETS_TOKEN")
