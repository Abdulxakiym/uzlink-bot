from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "64743910"))
CALL_CENTER = os.getenv("CALL_CENTER", "+998 (77) 177-10-01")
RADIUS_KM = int(os.getenv("RADIUS_KM", "300"))
DB_PATH = os.getenv("DB_PATH", "data/uzlink.sqlite3")
