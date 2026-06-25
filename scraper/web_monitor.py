import asyncio
import aiohttp
from bs4 import BeautifulSoup
from loguru import logger
from config import Config
from database.db import save_raw_message


async def _fetch_text(session: aiohttp.ClientSession, url: str) -> str:
    """Загружает страницу и возвращает чистый текст."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=12)) as resp:
            if resp.status != 200:
                return ""
            html = await resp.text(errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception:
        return ""


def _is_relevant(text: str) -> bool:
    text_lower = text.lower()
    has_kw = any(kw.lower() in text_lower for kw in Config.KEYWORDS)
    has_city = any(kw.lower() in text_lower for kw in Config.CITY_KEYWORDS)
    return has_kw and has_city


async def _scrape_site(session: aiohttp.ClientSession, site: dict):
    """Парсит главную страницу сайта и сохраняет релевантные ссылки."""
    try:
        async with session.get(site["url"], timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                return
            html = await resp.text(errors="ignore")

        soup = BeautifulSoup(html, "html.parser")
        base = site["url"].rstrip("/")

        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/"):
                href = base + href
            if base in href and len(href) > len(base) + 5:
                links.add(href)

        # Проверяем первые 15 ссылок
        for link in list(links)[:15]:
            text = await _fetch_text(session, link)
            if text and _is_relevant(text):
                msg_id = abs(hash(link)) % (10**9)
                # Ищем og:image на странице
                og_image = ""
                try:
                    async with session.get(link, timeout=aiohttp.ClientTimeout(total=10)) as r:
                        if r.status == 200:
                            soup2 = BeautifulSoup(await r.text(errors="ignore"), "html.parser")
                            tag = soup2.find("meta", property="og:image") or soup2.find("meta", attrs={"name": "og:image"})
                            if tag:
                                og_image = tag.get("content", "")
                except Exception:
                    pass
                is_new = await save_raw_message(msg_id, site["name"], text, link, media_url=og_image)
                if is_new:
                    logger.info(f"[WEB] {site['name']}: {link[:70]}")

    except Exception as e:
        logger.warning(f"[WEB] Ошибка {site['name']}: {e}")


async def run_web_scraper():
    """Каждые 30 минут обходит новостные сайты в поисках ЖКХ-новостей."""
    logger.info("Веб-скрапер запущен")
    while True:
        async with aiohttp.ClientSession(
            headers={"User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"}
        ) as session:
            tasks = [_scrape_site(session, site) for site in Config.NEWS_SITES]
            await asyncio.gather(*tasks)
        logger.debug("Веб-скрапер: цикл завершён, следующий через 30 мин")
        await asyncio.sleep(30 * 60)
