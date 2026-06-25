from openai import AsyncOpenAI
from config import Config
from loguru import logger

# Groq — бесплатный AI, OpenAI-совместимый API
_client = AsyncOpenAI(
    api_key=Config.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)
_MODEL = "llama-3.3-70b-versatile"


async def generate_clickbait_post(news_item: dict) -> tuple[str, str] | None:
    """Генерирует кликбейт-заголовок и пост. Возвращает (заголовок, текст) или None."""
    channel = news_item.get("channel", "")
    text = news_item.get("original_text", "")[:1500]
    url = news_item.get("source_url", "")

    prompt = f"""Ты — редактор вирусного новостного Telegram-канала об ЖКХ Астаны.

Исходное сообщение из @{channel}:
{text}

Источник: {url}

Напиши публикацию. Строго придерживайся формата.

ЗАГОЛОВОК (до 80 символов):
— Должен ШОКИРОВАТЬ и заставить кликнуть
— Используй цифры, масштаб, эмоции, угрозу
— Примеры: «В 5 районах Астаны лопнули трубы — сотни семей без воды», «Коммунальщики скрыли аварию сезона»
— Не врать, но максимально драматизировать реальные факты

ПОСТ (150–280 слов):
— Пиши как настоящий журналист: факты, адреса, последствия
— Абзац 1: кто пострадал и масштаб
— Абзац 2: подробности и хронология
— Абзац 3: реакция властей / прогноз
— Финал: тревожная нота или призыв следить за каналом
— Стиль: серьёзный, с ощущением срочности, умеренно эмодзи

Формат ответа (строго):
ЗАГОЛОВОК: [текст]
ПОСТ: [текст]"""

    try:
        response = await _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=900,
        )
        content = response.choices[0].message.content.strip()

        title, post_lines, in_post = "", [], False
        for line in content.split("\n"):
            if line.startswith("ЗАГОЛОВОК:"):
                title = line.replace("ЗАГОЛОВОК:", "").strip()
            elif line.startswith("ПОСТ:"):
                in_post = True
                rest = line.replace("ПОСТ:", "").strip()
                if rest:
                    post_lines.append(rest)
            elif in_post:
                post_lines.append(line)

        post_text = "\n".join(post_lines).strip()
        if not title or not post_text:
            logger.warning(f"Не удалось распарсить ответ AI")
            return None
        return title, post_text

    except Exception as e:
        logger.error(f"Ошибка генерации поста: {e}")
        return None


async def generate_morning_greeting() -> tuple[str, str]:
    """Генерирует утреннее приветствие. Возвращает (заголовок, текст)."""
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    weekday = weekdays[now.weekday()]

    prompt = f"""Ты — редактор Telegram-канала новостей Астаны.
Сегодня {date_str}, {weekday}.

Напиши тёплое утреннее приветствие для жителей Астаны.

ЗАГОЛОВОК (до 60 символов): бодрое, позитивное, с городом и днём
ПОСТ (80–120 слов): тёплое обращение, описание утреннего города, призыв следить за каналом. Стиль: дружелюбный, живой, с эмодзи.

Формат:
ЗАГОЛОВОК: [текст]
ПОСТ: [текст]"""

    try:
        response = await _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=400,
        )
        content = response.choices[0].message.content.strip()

        title, post_lines, in_post = "", [], False
        for line in content.split("\n"):
            if line.startswith("ЗАГОЛОВОК:"):
                title = line.replace("ЗАГОЛОВОК:", "").strip()
            elif line.startswith("ПОСТ:"):
                in_post = True
                rest = line.replace("ПОСТ:", "").strip()
                if rest:
                    post_lines.append(rest)
            elif in_post:
                post_lines.append(line)

        post_text = "\n".join(post_lines).strip()
        if not title:
            title = f"🌅 Доброе утро, Астана! {date_str}"
        if not post_text:
            post_text = "Начинаем новый день! Следите за нашим каналом 🏙️"
        return title, post_text

    except Exception as e:
        logger.error(f"Ошибка генерации приветствия: {e}")
        from datetime import datetime
        return (f"🌅 Доброе утро, Астана!", "Начинаем новый день! 🏙️")


async def generate_digest(news_items: list[dict]) -> str | None:
    """Суммарный дайджест для /digest."""
    if not news_items:
        return None
    formatted = "".join(
        f"\n--- {i}. @{item.get('channel','')} ---\n{item.get('original_text','')[:400]}\n"
        for i, item in enumerate(news_items, 1)
    )
    try:
        response = await _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": f"Краткий дайджест ЖКХ-новостей Астаны в 3-5 пунктах:\n{formatted}"}],
            temperature=0.6,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка дайджеста: {e}")
        return None
