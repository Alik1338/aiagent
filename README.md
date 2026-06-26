# aiagent
aiagent/
├── agent/              # AI-агент для обработки текста
├── bot/                # Telegram-бот
├── database/           # MongoDB интеграция
├── scraper/            # Веб-скрепер и мониторинг
├── utils/              # Утилиты и функции
├── config.py           # Конфигурация
├── main.py             # Главный файл
├── requirements.txt    # Зависимости
├── Dockerfile          # Docker контейнер
└── .env                # Переменные окружения

git clone https://github.com/Alik1338/aiagent.git
cd aiagent

python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

pip install -r requirements.txt

touch .env

# Telegram Bot Token (получить у @BotFather в Telegram)
TELEGRAM_BOT_TOKEN=xxxxxxxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Chat ID админки (где отправлять на проверку)
TELEGRAM_EDITOR_CHAT_ID=123456789

# ID канала для публикации одобренных новостей
PUBLISH_CHANNEL_ID=@your_channel_name

# Для Telethon (чтение постов из Telegram-каналов)
API_ID=123456
API_HASH=abcdefghijklmnopqrstuvwxyz123456

# Номер телефона для Telethon сессии
PHONE=+1234567890

# Сессионная строка Telethon (или оставить пустым, сгенерируется)
TELETHON_SESSION_STRING=

# MongoDB Atlas подключение
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/dbname

# API ключи для генерации текста
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
XAI_API_KEY=xai-xxxxxxxxxxxxx

Шаг 5: Настроить переменные окружения


TELEGRAM_BOT_TOKEN:

Напиши @BotFather в Telegram
Отправь /newbot
Следуй инструкциям, скопируй токен



TELEGRAM_EDITOR_CHAT_ID:

Отправь сообщение боту
Используй скрипт для получения ID:

# Добавь в main.py временно:
     # print(f"Chat ID: {message.chat.id}")

     MongoDB URI:

Регистрируйся на https://cloud.mongodb.com
Создай кластер Free tier
Скопируй connection string



GROQ API Key:

Зайди на https://console.groq.com
Создай API key (бесплатный)



Telethon сессия (для чтения Telegram-каналов):

python generate_session.py
   # Введи номер телефона и код из Telegram

   python main.py

   docker build -t aiagent .

   docker run --env-file .env aiagent

   docker-compose up

   Команды Telegram-бота

После запуска бот принимает команды:

КомандаОписаниеКто может/startПоказать справкуВсе/checkПолучить новости на проверкуТолько админы/morningСоздать утреннее приветствиеТолько админы

Администраторы указаны в config.py:

ADMINS = ["Mr0trenbolone","kzvitaliy","papqas"]  # добавь свой username

Как работает система

1️⃣ Сбор новостей (Scraper)


Web Scraper (scraper/web_monitor.py) - скрепит новостные сайты:

Tengrinews
Informburo
Zakon.kz
Nur.kz
Orda.kz



Telegram Monitor (scraper/telegram_monitor.py) - мониторит Telegram-каналы


Ищет новости с ключевыми словами (ЖКХ, отопление, авария и т.д.)

2️⃣ Обработка текста (Agent)


agent/news_agent.py - использует Groq или xAI API
Генерирует:

Привлекательные заголовки
Краткое описание новости
Утреннее приветствие





3️⃣ Хранение данных (Database)


MongoDB хранит найденные новости
Статусы: pending, approved, rejected
История для аналитики


4️⃣ Модерация (Bot)


Админ получает новости на проверку
Может одобрить (✅) или отклонить (❌)
Одобренные идут в канал публикации


5️⃣ Публикация (Publisher)


Публикует одобренные новости в Telegram-канал
Может добавлять изображения

pip install -r requirements.txt

