from telethon import TelegramClient, events
from telethon.sessions import StringSession
from config import Config
from database.db import save_raw_message
from loguru import logger

_session = StringSession(Config.TELETHON_SESSION_STRING) if Config.TELETHON_SESSION_STRING else "zhkh_session"
client = TelegramClient(_session, Config.API_ID, Config.API_HASH)


def _is_relevant(text: str) -> bool:
    text_lower = text.lower()
    has_zhkh = any(kw.lower() in text_lower for kw in Config.KEYWORDS)
    has_city = any(kw.lower() in text_lower for kw in Config.CITY_KEYWORDS)
    return has_zhkh and has_city


def _get_media_type(message) -> str:
    """Определяет тип медиа в сообщении."""
    if message.video or (message.document and getattr(message.document, "mime_type", "").startswith("video")):
        return "video"
    if message.photo:
        return "photo"
    return "none"


@client.on(events.NewMessage())
async def on_new_message(event):
    try:
        if not event.chat:
            return
        channel_username = getattr(event.chat, "username", None) or str(event.chat_id)
        if channel_username not in Config.TG_CHANNELS:
            return

        text = event.message.message or ""
        if not text or not _is_relevant(text):
            return

        message_id = event.message.id
        url = f"https://t.me/{channel_username}/{message_id}"
        media_type = _get_media_type(event.message)

        is_new = await save_raw_message(
            message_id, channel_username, text, url,
            media_type=media_type,
        )
        if is_new:
            logger.info(f"[{media_type}] @{channel_username}/{message_id} — {text[:60]}...")
    except Exception as e:
        logger.warning(f"Ошибка обработки сообщения: {e}")


async def download_media(channel: str, message_id: int) -> tuple[bytes | None, str]:
    """
    Скачивает фото или видео из оригинального Telegram-сообщения.
    Возвращает (байты, тип) — ("photo"/"video"/"none").
    """
    try:
        messages = await client.get_messages(channel, ids=message_id)
        if not messages or not messages.media:
            return None, "none"

        media_type = _get_media_type(messages)
        if media_type == "none":
            return None, "none"

        data = await client.download_media(messages.media, bytes)
        return data, media_type
    except Exception as e:
        logger.warning(f"Не удалось скачать медиа @{channel}/{message_id}: {e}")
        return None, "none"


async def start_telethon():
    await client.start(phone=Config.PHONE)

    valid = []
    for ch in Config.TG_CHANNELS:
        try:
            await client.get_entity(ch)
            valid.append(ch)
        except Exception:
            logger.warning(f"Канал @{ch} не найден — пропускаем")

    Config.TG_CHANNELS = valid
    logger.success(f"Telethon запущен. Слушаем {len(valid)} каналов.")
    await client.run_until_disconnected()
