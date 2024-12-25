# run.py

import asyncio 
import logging
from config import API_TOKEN
from aiogram import Bot, Dispatcher
from app.handlers import router
from app.database.models import async_main

from sqlalchemy import select, update
from app.database.models import Subscription, async_session
from datetime import datetime, timedelta
import app.keyboards as kb

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


async def main():
    await async_main()
    dp.include_router(router)
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')