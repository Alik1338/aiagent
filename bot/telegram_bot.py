import html
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import Config
from loguru import logger
import utils.state as state

bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


def is_admin(username: str) -> bool:
    return username in Config.ADMINS


def build_review_keyboard(news_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"approve:{news_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{news_id}"),
    ]])


async def send_for_review(
    bot: Bot,
    news_id: str,
    title: str,
    post_text: str,
    image_url: str | None = None,
    source_url: str = "",
    channel: str = ""
):
    """Отправляет новость администратору на проверку"""
    target = state.load()
    if not target:
        logger.error("Не найден chat_id администратора!")
        return

    caption = (
        f"🔴 <b>{html.escape(title)}</b>\n\n"
        f"{html.escape(post_text[:800])}\n\n"
        f"📢 @{html.escape(channel)}"
        + (f"\n🔗 <a href='{source_url}'>Оригинал</a>" if source_url else "")
    )

    keyboard = build_review_keyboard(news_id)

    try:
        if image_url:
            await bot.send_photo(chat_id=target, photo=image_url, caption=caption, parse_mode="HTML", reply_markup=keyboard)
        else:
            await bot.send_message(chat_id=target, text=caption, parse_mode="HTML", reply_markup=keyboard, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Ошибка отправки на ревью: {e}")


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 <b>ЖКХ Дайджест Астаны</b>\n\n"
        "Команды:\n"
        "/check — получить новости на проверку\n"
        "/morning — утреннее приветствие",
        parse_mode="HTML"
    )


@dp.message(Command("check"))
async def check_news(message: types.Message):
    if not is_admin(message.from_user.username or ""):
        await message.answer("⛔ У тебя нет доступа")
        return

    await message.answer("⏳ Ищу новости...")

    from database.db import get_pending_news
    from agent.news_agent import generate_clickbait_post

    items = await get_pending_news(limit=5)

    if not items:
        await message.answer("📭 Новостей пока нет.")
        return

    sent = 0
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
            channel=item.get("channel", "news")
        )
        sent += 1

    await message.answer(f"✅ Отправлено на ревью: {sent} новостей")


async def run_bot():
    logger.info("🤖 Бот запущен")
    await dp.start_polling(bot)