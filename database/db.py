from loguru import logger
from datetime import datetime

# Временно отключаем MongoDB
_db = None

async def init_db():
    global _db
    logger.warning("⚠️ MongoDB отключена временно (SSL проблема)")
    logger.info("Бот будет работать без сохранения новостей в базу")
    # Здесь можно добавить in-memory хранилище позже


async def save_raw_message(
    message_id: int,
    channel: str,
    text: str,
    url: str,
    media_type: str = "none",
    media_url: str = "",
) -> bool:
    logger.info(f"[MOCK] Сохранена новость: {channel} - {text[:80]}...")
    return True


async def get_pending_news(limit: int = 5):
    return []  # пока нет новостей


async def set_review_content(news_id: str, title: str, post_text: str, image_url: str | None):
    pass


async def set_news_status(news_id: str, status: str):
    pass


async def get_news_by_id(news_id: str):
    return None