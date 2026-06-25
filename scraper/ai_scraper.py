import asyncio
import aiohttp
from bs4 import BeautifulSoup

from database.db import save_news


SITES = [
    "https://tengrinews.kz",
    "https://www.zakon.kz",
    "https://informburo.kz"
]


KEYWORDS = [
    "жкх", "отопление", "вода", "авария",
    "теплосеть", "электричество", "отключение",
    "ремонт", "коммунал", "канализация"
]


def is_relevant(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in KEYWORDS)


def get_og_image(soup):
    tag = soup.find("meta", property="og:image")
    if tag:
        return tag.get("content")
    return None


async def parse_page(session, url):

    try:
        async with session.get(url, timeout=10) as resp:
            html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.text if soup.title else url
        text = soup.get_text()

        if not is_relevant(title + text):
            return

        image = get_og_image(soup)

        await save_news(
            title=title,
            original_text=text[:1500],
            generated_text=text[:1500],
            channel="AI SCRAPER",
            source_url=url,
            image=image
        )

        print("✅ NEWS FOUND:", title)

    except Exception as e:
        print("❌ ERROR:", url, e)


async def crawl_site(session, base_url):

    try:
        async with session.get(base_url, timeout=10) as resp:
            html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")

        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if href.startswith("/"):
                href = base_url + href

            if base_url in href:
                links.add(href)

        tasks = [parse_page(session, link) for link in list(links)[:10]]

        await asyncio.gather(*tasks)

    except Exception as e:
        print("❌ SITE ERROR:", base_url, e)


async def run_ai_scraper():

    print("🧠 AI SCRAPER STARTED")

    while True:

        async with aiohttp.ClientSession() as session:

            tasks = [crawl_site(session, site) for site in SITES]
            await asyncio.gather(*tasks)

        await asyncio.sleep(300)