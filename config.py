from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_EDITOR_CHAT_ID = int(os.getenv("TELEGRAM_EDITOR_CHAT_ID", 0))

    # Канал для публикации одобренных новостей (можно @username или числовой ID)
    _pub = os.getenv("PUBLISH_CHANNEL_ID", "")
    PUBLISH_CHANNEL_ID = int(_pub) if _pub.lstrip("-").isdigit() else _pub

    # Администраторы — только они могут одобрять/отклонять
    ADMINS = ["Mr0trenbolone","kzvitaliy","papqas"]  # добавляй сюда username без @

    # Telethon (чтение каналов)
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH")
    PHONE = os.getenv("PHONE")
    TELETHON_SESSION_STRING = os.getenv("TELETHON_SESSION_STRING", "")

    # xAI (оставлен как запасной)
    XAI_API_KEY = os.getenv("XAI_API_KEY")

    # Groq — бесплатный AI для генерации текста (console.groq.com)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # MongoDB Atlas
    MONGODB_URI = os.getenv("MONGODB_URI")

    # Интервал проверки новостей (2 часа)
    DIGEST_INTERVAL_SECONDS = 2 * 3600

    # Максимум новостей за один цикл ревью
    MAX_REVIEW_BATCH = 5

    # Ключевые слова для фильтрации ЖКХ-новостей
    KEYWORDS = [
        # ЖКХ
        "ЖКХ", "коммунальн", "отопление", "водоснабж", "канализация",
        "прорыв", "авария", "отключение", "тариф", "ОСИ", "КСК",
        "управляющ", "многоквартирн", "трубы", "лифт", "электроснабж",
        "теплоснабж", "мусор", "вывоз", "двор", "подъезд", "УК ",
        "теплосеть", "водоканал", "теплоцентраль", "горячая вода",
        "холодная вода", "отключили", "прорвало", "затопило",
        # Город и инфраструктура
        "дорог", "ремонт дороги", "яма", "асфальт", "парковк",
        "пробк", "перекрыт", "светофор", "транспорт", "маршрут",
        "школ", "больниц", "поликлиник", "детский сад",
        # Безопасность
        "пожар", "взрыв", "обрушени", "задымлени",
        "МЧС", "скорая", "полиция", "криминал",
        # Экология и природа
        "загрязнени", "смог", "пыль", "паводок", "наводнени",
    ]

    # Ключевые слова для фильтрации по городу Астана
    CITY_KEYWORDS = [
        "Астана", "астан", "Нур-Султан", "нур-султан",
        "столиц", "акимат",
    ]

    # Telegram-каналы для мониторинга (расширенный список)
    TG_CHANNELS = [
        # Крупные КЗ СМИ (проверенные)
        "tengrinews",
        "informburo_kz",
        "nurnews",
        "24kz",
        "orda_kz",
        "zakon_kz",
        "egemen_kz",
        "kursiv_media",
        # Астана официальные
        "astana_akimat",
        "astanatv",
    ]

    # Сайты для веб-скрапинга
    NEWS_SITES = [
        {"name": "Tengrinews", "url": "https://tengrinews.kz/"},
        {"name": "Informburo", "url": "https://informburo.kz/"},
        {"name": "Zakon.kz",   "url": "https://www.zakon.kz/"},
        {"name": "Nur.kz",     "url": "https://www.nur.kz/"},
        {"name": "Orda.kz",    "url": "https://orda.kz/"},
    ]
