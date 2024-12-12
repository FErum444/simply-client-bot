import logging
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import (API_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL)
from app.handlers import router
from app.database.models import async_main

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def on_startup(app: web.Application):
    """Действия при старте приложения."""
    await async_main()  # Подключение базы данных или выполнение других задач инициализации
    dp.include_router(router)  # Регистрация маршрутов хендлеров
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)
    logging.info("Webhook установлен успешно.")


async def on_shutdown(app: web.Application):
    """Действия при остановке приложения."""
    logging.info("Удаление вебхука...")
    await bot.delete_webhook()
    await bot.session.close()  # Корректное закрытие HTTP-сессии


def main() -> None:
    """Основная точка входа в приложение."""
    # Создание и настройка приложения aiohttp
    app = web.Application()

    # Регистрация событий старта и завершения
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Настройка webhook
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # Запуск веб-сервера
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        main()
    except KeyboardInterrupt:
        print("Завершение работы.")
