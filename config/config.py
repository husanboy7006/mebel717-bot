import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Admin ID larni vergul bilan ajratilgan ro'yxatdan integer array ga o'tkazamiz
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",") if admin_id]
DB_URL = os.getenv("DB_URL")
GROUP_ID = os.getenv("GROUP_ID")
if GROUP_ID:
    GROUP_ID = int(GROUP_ID)
