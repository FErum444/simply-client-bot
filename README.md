
# Simply VPN Telegram Бот

Простой Telegram-бот для продажи подписок на VPN-сервис "Simply VPN"

## Установка

1. **Клонирование репозитория:**

    ```bash
    git clone https://github.com/FErum444/simply-client-bot.git
    cd simply-client-bot
    ```

2. **Создание виртуального окружения:**

    ```bash
    sudo apt install -y python3-venv 
    python3 -m venv .venv
    source .venv/bin/activate  # Для Windows: .venv\Scripts\activate
    ```

3. **Установка зависимостей:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Настройка конфигурации:**

    - Создайте файл `.env` в корне проекта.
    - Добавьте ваш Telegram-бот токен и другие данные:

    ```env
    API_TOKEN=your_telegram_bot_token_here
    MAIN_WALLET=your_ton_wallet
    ADMIN_ID=your_telegram_id
    DB_URI=sqlite+aiosqlite:///db.sqlite3
    THRESHOLD=0.01

    WEB_SERVER_HOST=127.0.0.1
    WEB_SERVER_PORT=8443
    WEBHOOK_PATH=/webhook
    WEBHOOK_SECRET=your_webhook_secret
    BASE_WEBHOOK_URL=https://example.com
    ```

5. **Инициализация базы данных:**

    При первом запуске бота база данных будет автоматически создана и инициализирована.


## Запуск бота

Инструкция для настройки через systemd

1. **Создайте systemd unit-файл:**

    - Создайте файл сервиса, например, `/etc/systemd/system/simply-client-bot.service`

    ```bash
    sudo nano /etc/systemd/system/simply-client-bot.service
    ```

2. **Заполните содержимое unit-файла:**

    - Пример файла сервиса
        
    ```ini
    [Unit]
    Description=Simply VPN Bot
    After=network.target

    [Service]
    User=USERNAME
    WorkingDirectory=/home/USERNAME/simply-client-bot
    ExecStart=/home/USERNAME/simply-client-bot/.venv/bin/python /home/USERNAME/simply-client-bot/run.py
    Restart=always
    RestartSec=5
    Environment=PYTHONUNBUFFERED=1

    [Install]
    WantedBy=multi-user.target
    ```

3. **Перезагрузите `systemd` для применения изменений:**

    - Выполните команду

    ```bash
    sudo systemctl daemon-reload
    ```

4. **Запустите сервис**

    ```bash
    sudo systemctl start simply-client-bot
    ```

5. **Добавьте бот в автозагрузку**

    ```bash
    sudo systemctl enable simply-client-bot
    ```

6. **Проверка статуса сервиса**

    - Убедитесь, что бот работает

    ```bash
    sudo systemctl status simply-client-bot
    ```


## Если нужно внести изменения или доработать код бота, выполните

- Остановите сервис:

    ```bash
    sudo systemctl stop simply-client-bot
    ```

- Внесите изменения.
- Перезапустите:

    ```bash
    sudo systemctl restart simply-client-bot
    ```