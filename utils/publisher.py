import re
import aiohttp
from scraper.telegram_monitor import client as tg
from config import Config
from loguru import logger


async def publish_via_telethon(title: str, post_text: str, image_url: str | None, source_url: str):
    """Публикует пост через Telethon (user account) — не требует прав бота в канале."""
    text = f"🔴 **{title}**\n\n{post_text}"
    if source_url:
        text += f"\n\n🔗 {source_url}"

    channel = Config.PUBLISH_CHANNEL_ID

    try:
        if image_url:
            # Скачиваем картинку и отправляем байтами
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        image_bytes = await resp.read()
                        await tg.send_file(channel, image_bytes, caption=text, parse_mode="markdown")
                        logger.success(f"Опубликовано с картинкой: {title[:60]}")
                        return

        await tg.send_message(channel, text, parse_mode="markdown")
        logger.success(f"Опубликовано (без картинки): {title[:60]}")

    except Exception as e:
        logger.error(f"Ошибка публикации через Telethon: {e}")


async def join_by_invite(link: str) -> str:
    """Вступает в канал/группу по ссылке-приглашению через Telethon."""
    try:
        link = link.strip()
        # Формат: t.me/+HASH или t.me/joinchat/HASH
        if re.search(r't\.me/\+|joinchat', link):
            hash_part = re.search(r'(?:joinchat/|\+)([a-zA-Z0-9_-]+)', link)
            if hash_part:
                from telethon.tl.functions.messages import ImportChatInviteRequest
                await tg(ImportChatInviteRequest(hash_part.group(1)))
                logger.success(f"Вступил по invite: {link}")
                return "✅ Вступил в канал/группу по ссылке!"
        else:
            # Публичный канал: t.me/username
            username = link.rstrip("/").split("/")[-1]
            from telethon.tl.functions.channels import JoinChannelRequest
            await tg(JoinChannelRequest(username))
            logger.success(f"Вступил в @{username}")
            return f"✅ Вступил в @{username}!"

    except Exception as e:
        logger.error(f"Ошибка вступления: {e}")
        return f"❌ Не удалось вступить: {e}"
