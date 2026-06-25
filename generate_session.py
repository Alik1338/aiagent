"""
Запусти ОДИН РАЗ локально перед деплоем на Render.
Скопируй напечатанную строку и вставь как TELETHON_SESSION_STRING
в .env и в переменные окружения Render.
"""
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

print("Авторизация в Telegram...")
with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    client.start(phone=PHONE)
    session_string = client.session.save()

print("\n" + "=" * 60)
print("Скопируй строку ниже и вставь как TELETHON_SESSION_STRING:")
print("=" * 60)
print(session_string)
print("=" * 60 + "\n")
