import asyncio
import html
import re
from dotenv import load_dotenv
from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery

from config import Config
from database.db import init_db, get_news_by_id, set_news_status
from scraper.telegram_monitor import start_telethon
from scraper.web_monitor import run_web_scraper
from utils.auto_sender import run_review_scheduler
from utils.publisher import publish_via_telethon
from bot.telegram_bot import is_admin, send_for_review
import utils.state as state

load_dotenv()

bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def handle_commands(message: Message):
    username = message.from_user.username or ""
    text = message.text or ""

    if is_admin(username):
        state.save(message.chat.id)

    if text == "/start":
        await message.answer(
            "👋 <b>ЖКХ Дайджест Астаны</b>\n\n"
            "Команды:\n"
            "/check — получить новости на проверку\n"
            "/morning — утреннее приветствие",
            parse_mode="HTML",
        )

    elif text == "/check":
        if not is_admin(username):
            await message.answer("⛔ Нет доступа")
            return

        await message.answer("⏳ Ищу новости...")

        from database.db import get_pending_news
        from agent.news_agent import generate_clickbait_post

        items = await get_pending_news(limit=5)

        if not items:
            # Демо новости
            demo = [
                {
                    "title": "В Астане прорвало теплотрассу на Мангилик Ел",
                    "post_text": "Сегодня утром в районе Есиль произошел крупный прорыв трубы. Без отопления остались несколько многоэтажек. Аварийные службы работают.",
                    "channel": "tengrinews",
                    "source_url": "https://tengrinews.kz"
                }
            ]
            for i, item in enumerate(demo):
                await send_for_review(
                    bot=bot,
                    news_id=f"demo_{i}",
                    title=item["title"],
                    post_text=item["post_text"],
                    source_url=item["source_url"],
                    channel=item["channel"]
                )
            return

        for item in items:
            result = await generate_clickbait_post(item)
            if not result:
                continue
            title, post_text = result
            await send_for_review(
                bot=bot,
                news_id=item["_id"],
                title=title,
                post_text=post_text,
                source_url=item.get("source_url", ""),
                channel=item.get("channel", "")
            )

    elif text == "/morning":
        if not is_admin(username):
            await message.answer("⛔ Нет доступа")
            return

        await message.answer("🌅 Генерирую утреннее приветствие...")

        from agent.news_agent import generate_morning_greeting
        from utils.image_gen import generate_morning_image

        title, post_text = await generate_morning_greeting()
        image_url = await generate_morning_image()

        await send_for_review(
            bot=bot,
            news_id="morning",
            title=title,
            post_text=post_text,
            image_url=image_url,
            source_url="",
            channel="Утренний дайджест"
        )


@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    username = callback.from_user.username or ""
    if not is_admin(username):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    data = callback.data or ""
    if ":" not in data:
        return

    action, news_id = data.split(":", 1)
    msg = callback.message

    if action == "reject":
        if news_id != "morning":
            await set_news_status(news_id, "rejected")
        await msg.edit_reply_markup(reply_markup=None)
        await callback.answer("❌ Отклонено")
        return

    if action == "approve":
        caption = msg.caption or msg.text or ""
        
        # Публикуем в канал
        await publish_via_telethon(
            title="Опубликовано",
            post_text=caption,
            image_url=None,
            source_url=""
        )

        await msg.edit_reply_markup(reply_markup=None)
        await callback.answer("✅ Опубликовано в канал!")


async def main():
    await init_db()
    logger.info("🚀 Запуск агента ЖКХ Астаны...")
    await asyncio.gather(
        start_telethon(),
        run_web_scraper(),
        run_review_scheduler(bot),
        dp.start_polling(bot),
    )


if __name__ == "__main__":
    asyncio.run(main())