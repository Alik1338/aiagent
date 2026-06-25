import asyncio
import html
from aiogram import Bot
from aiogram.types import BufferedInputFile
from database.db import get_pending_news, set_review_content
from agent.news_agent import generate_clickbait_post, generate_morning_greeting
from utils.image_gen import generate_morning_image
from bot.telegram_bot import send_for_review, build_review_keyboard
from config import Config
from loguru import logger
import utils.state as state


async def run_review_scheduler(bot: Bot):
    """Каждые 2 часа берёт новые новости и отправляет на ревью."""
    logger.info("Планировщик ревью запущен")
    while True:
        await asyncio.sleep(Config.DIGEST_INTERVAL_SECONDS)
        await process_pending_news(bot)


async def _get_source_media(item: dict) -> tuple[bytes | None, str | None, str]:
    """
    Получает медиа из источника новости.
    Возвращает (bytes_или_none, url_или_none, media_type).
    """
    media_type = item.get("media_type", "none")
    media_url = item.get("media_url", "")
    channel = item.get("channel", "")
    message_id = item.get("message_id")

    # Для Telegram-сообщений с медиа — скачиваем через Telethon
    if media_type in ("photo", "video") and message_id and channel:
        try:
            from scraper.telegram_monitor import download_media
            data, mtype = await download_media(channel, int(message_id))
            if data:
                return data, None, mtype
        except Exception as e:
            logger.warning(f"Не удалось скачать медиа: {e}")

    # Для веб-статей — берём og:image URL
    if media_url:
        return None, media_url, "photo"

    return None, None, "none"


async def _send_review_with_media(
    bot: Bot,
    news_id: str,
    caption: str,
    media_bytes: bytes | None,
    media_url: str | None,
    media_type: str,
    chat_id: int,
):
    """Отправляет новость на ревью с реальным медиа из источника."""
    keyboard = build_review_keyboard(news_id)

    # Приоритет: байты (Telegram медиа) > URL (og:image) > только текст
    if media_bytes:
        file = BufferedInputFile(media_bytes, filename=f"media.{'mp4' if media_type == 'video' else 'jpg'}")
        try:
            if media_type == "video":
                await bot.send_video(chat_id=chat_id, video=file, caption=caption, parse_mode="HTML", reply_markup=keyboard)
            else:
                await bot.send_photo(chat_id=chat_id, photo=file, caption=caption, parse_mode="HTML", reply_markup=keyboard)
            return
        except Exception as e:
            logger.warning(f"Ошибка отправки медиа из байтов: {e}")

    if media_url:
        try:
            await bot.send_photo(chat_id=chat_id, photo=media_url, caption=caption, parse_mode="HTML", reply_markup=keyboard)
            return
        except Exception as e:
            logger.warning(f"Ошибка отправки og:image: {e}")

    # Fallback — только текст с кнопками
    await bot.send_message(chat_id=chat_id, text=caption, parse_mode="HTML", reply_markup=keyboard, disable_web_page_preview=True)


async def _process_one(bot: Bot, item: dict, chat_id: int) -> bool:
    news_id = item["_id"]
    try:
        result = await generate_clickbait_post(item)
        if not result:
            logger.warning(f"Пропущена {news_id} — AI не вернул результат")
            return False

        title, post_text = result
        channel = item.get("channel", "")
        source_url = item.get("source_url", "")

        # Получаем медиа из источника
        media_bytes, media_url, media_type = await _get_source_media(item)

        # Сохраняем в БД
        await set_review_content(news_id, title, post_text, media_url or "")

        caption = (
            f"🔴 <b>{html.escape(title)}</b>\n\n"
            f"{html.escape(post_text[:750])}{'...' if len(post_text) > 750 else ''}\n\n"
            f"📢 @{html.escape(channel)}"
            + (f"\n🔗 <a href='{source_url}'>Оригинал</a>" if source_url else "")
        )

        await _send_review_with_media(bot, news_id, caption, media_bytes, media_url, media_type, chat_id)
        return True

    except Exception as e:
        logger.error(f"Ошибка при обработке {news_id}: {e}")
        return False


async def process_pending_news(bot: Bot, chat_id: int = 0) -> str:
    try:
        target = chat_id or state.load()
        items = await get_pending_news(limit=Config.MAX_REVIEW_BATCH)

        if not items:
            logger.info("Новостей нет — генерирую утреннее приветствие")
            title, post_text = await generate_morning_greeting()
            image_url = await generate_morning_image()
            await send_for_review(
                bot=bot, news_id="morning",
                title=title, post_text=post_text,
                image_url=image_url, source_url="", channel="Доброе утро",
                chat_id=target,
            )
            return "🌅 Новостей пока нет — отправил утреннее приветствие на проверку."

        logger.info(f"Обрабатываю {len(items)} новостей параллельно...")
        results = await asyncio.gather(*[_process_one(bot, item, target) for item in items])

        sent = sum(results)
        logger.success(f"Отправлено на ревью: {sent}/{len(items)}")
        return f"✅ Готово! Отправлено на ревью: {sent} новост{'ь' if sent == 1 else 'и' if 2 <= sent <= 4 else 'ей'}."

    except Exception as e:
        logger.error(f"Ошибка при обработке новостей: {e}")
        return f"❌ Ошибка: {e}"
