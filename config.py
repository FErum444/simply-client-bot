# config.py

from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

# Токен для бота
API_TOKEN = os.getenv('API_TOKEN')

# Кошелек для приема платежей
MAIN_WALLET = os.getenv('MAIN_WALLET')

# Идентификатор администратора (если нужен)
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))  # Второй аргумент — значение по умолчанию, если переменная отсутствует

# Параметры подключения к базе данных (если будет использоваться база данных)
DB_URI = os.getenv('DB_URI', 'sqlite+aiosqlite:///db.sqlite3')

# Трешход в процентах - для проверки отклонения суммы платежа
THRESHOLD = float(os.getenv('THRESHOLD', 0.01))

WEB_SERVER_HOST = os.getenv('WEB_SERVER_HOST', '127.0.0.1')
WEB_SERVER_PORT = int(os.getenv('WEB_SERVER_PORT', 8443))
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/webhook')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
BASE_WEBHOOK_URL = os.getenv('BASE_WEBHOOK_URL')
