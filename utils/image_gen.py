import urllib.parse
import random
from loguru import logger

# Pollinations.ai — полностью бесплатная генерация картинок, ключ не нужен


def _make_url(prompt: str, width: int = 1024, height: int = 576) -> str:
    seed = random.randint(1, 99999)
    encoded = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={seed}"


async def generate_news_image(title: str, post_text: str) -> str | None:
    """Генерирует кликбейтную картинку для новости."""
    prompt = (
        f"dramatic news photo Kazakhstan utilities crisis, {title[:100]}, "
        "burst pipe flooding street, emergency workers at night, dark frozen apartments, "
        "dramatic lighting, photojournalism style, cinematic, no text"
    )
    url = _make_url(prompt)
    logger.info(f"Картинка новости: {url[:80]}...")
    return url


async def generate_morning_image() -> str | None:
    """Генерирует утреннюю картинку Астаны."""
    prompt = (
        "beautiful golden sunrise over Astana Kazakhstan skyline, "
        "Baiterek tower, modern city, warm orange pink sky, peaceful morning, "
        "aerial view, cinematic quality, photorealistic, no text"
    )
    url = _make_url(prompt)
    logger.info(f"Утренняя картинка: {url[:80]}...")
    return url
