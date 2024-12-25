# run.py

import logging
import sys


from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import (API_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL)
from app.handlers import router
from app.database.models import async_main

import asyncio
from app.database.models import Subscription, async_session
from sqlalchemy import select, update
from datetime import datetime, timedelta
import app.keyboards as kb


# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()





# Функция для отправки уведомлений
async def send_notification(tg_id: int, message: str):
    try:
        await bot.send_message(chat_id=tg_id, text=message, reply_markup=await kb.inline_buttons(), parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения пользователю {tg_id}: {e}")

# Проверка и исправление статуса подписок
async def check_and_update_subscriptions():
    async with async_session() as session:
        # Выбор всех активных подписок
        result = await session.scalars(select(Subscription).where(Subscription.status == True))
        subscriptions = result.all()
        if not subscriptions:
            return
        
        now = datetime.utcnow()
        for sub in subscriptions:
            issue_date = datetime.strptime(sub.issue_date, "%Y-%m-%d %H:%M:%S")
            expiration_date = issue_date + timedelta(days=sub.duration * 30)  # Примерно 30 дней в месяце
            
            # Если срок истёк, обновляем статус
            if now > expiration_date:
                sub.status = False
                logging.info(f"Подписка {sub.id} помечена как неактивная.")
                await session.commit()
                

# Уведомления о сроках подписки
async def send_subscription_reminders():
    async with async_session() as session:
        result = await session.scalars(select(Subscription).where(Subscription.status == True))
        subscriptions = result.all()
        if not subscriptions:
            return
        
        now = datetime.utcnow()
        reminders = {
            "week": timedelta(days=7),
            "3_days": timedelta(days=3),
            "1_day": timedelta(days=1),
            # "1_minute": timedelta(minutes=1),
        }
        
        for sub in subscriptions:
            issue_date = datetime.strptime(sub.issue_date, "%Y-%m-%d %H:%M:%S")
            expiration_date = issue_date + timedelta(days=sub.duration * 30)
            remaining_time = expiration_date - now
            
            if reminders["week"] <= remaining_time < reminders["week"] + timedelta(hours=1):
                await send_notification(sub.tg_id, "Ваши подписки истекают через неделю!")
            elif reminders["3_days"] <= remaining_time < reminders["3_days"] + timedelta(hours=1):
                await send_notification(sub.tg_id, "Ваши подписки истекают через 3 дня!")
            elif reminders["1_day"] <= remaining_time < reminders["1_day"] + timedelta(hours=1):
                await send_notification(sub.tg_id, "Ваши подписки истекают завтра!")
            # elif reminders["1_minute"] <= remaining_time < reminders["1_minute"] + timedelta(seconds=30):
            #     await send_notification(sub.tg_id, "Ваши подписки истекают через минуту!")

# Шедулер
async def scheduler():
    while True:
        await check_and_update_subscriptions()
        await send_subscription_reminders()
        await asyncio.sleep(24 * 60 * 60)
        # await asyncio.sleep(1 * 60)








async def on_startup(app: web.Application):
    """Действия при старте приложения."""
    await async_main()  # Подключение базы данных или выполнение других задач инициализации
    dp.include_router(router)  # Регистрация маршрутов хендлеров
    asyncio.create_task(scheduler())
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
