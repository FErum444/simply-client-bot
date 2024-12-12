
# Simply VPN Telegram Бот

Простой Telegram-бот для продажи подписок на VPN-сервис "Simply VPN"

## Установка

1. **Клонирование репозитория:**

    ```bash
    git clone https://github.com/yourusername/simply_vpn_bot.git
    cd simply_vpn_bot
    ```

2. **Создание виртуального окружения:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Для Windows: .venv\Scripts\activate
    ```

3. **Установка зависимостей:**

    ```bash
    pip install -r requirements.txt
    ```
4. **Настройка конфигурации:**

    - Создайте файл `.env` в корне проекта.
    - Добавьте ваш Telegram-бот токен:

        ```env
        API_TOKEN=your_telegram_bot_token_here
        MAIN_WALLET=your_ton_wallet
        ADMIN_ID=your_telegram_id
        DB_URI=sqlite+aiosqlite:///db.sqlite3
        THRESHOLD=0.01
        ```

5. **Инициализация базы данных:**

    При первом запуске бота база данных будет автоматически создана и инициализирована.

6. **Запуск бота:**

    ```bash
    python bot.py
    ```
