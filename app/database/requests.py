# requests.py

from app.database.models import async_session
from app.database.models import User, Plan, Bill, Subscription
from sqlalchemy import select, func # exists, update, delete

async def set_user(tg_id, username, first_name, last_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                signup_date = func.now()))
            await session.commit()

async def get_plans():
    async with async_session() as session:
        return await session.scalars(select(Plan))
    
async def get_plan(plan_id):
    async with async_session() as session:
        return await session.scalar(select(Plan).where(Plan.id == plan_id))

async def add_bill(tg_id, bill_number, status, plan, price, pay_link):
    async with async_session() as session:
        
        session.add(Bill(tg_id=tg_id, bill_number=bill_number, status=status, plan=plan, price=price, pay_link=pay_link, issue_date=func.now()))
        await session.commit()

async def update_bill_status(bill_number: int, new_status: bool):
    async with async_session() as session:
        bill = await session.scalar(select(Bill).where(Bill.bill_number == bill_number))
        if bill:
            bill.status = new_status
            bill.paid_date = func.now()
            await session.commit()

async def set_subscription(tg_id, bill_number, plan, duration, payment_info):
    async with async_session() as session:
        session.add(Subscription(tg_id=tg_id, status=True, bill_number=bill_number, plan=plan, duration=duration, payment_info=payment_info, issue_date = func.now()))
        await session.commit()

async def get_active_subscriptions(tg_id):
    async with async_session() as session:
        result = await session.scalars(select(Subscription).where(Subscription.tg_id == tg_id, Subscription.status == True))
        if result:
            return result.all()
        else:
            return []

async def check_free_bill_exists(tg_id: int):
    async with async_session() as session:
        query = select(Bill).where(Bill.tg_id == tg_id, Bill.price == 0, Bill.status == True)
        result = await session.execute(query)
        
        # Возвращаем True, если запись существует, иначе False
        return result.scalar() is not None





description_0 = (
    "1 месяц — Исследователь 🧭\n\n"
    "Пробуй интернет без границ бесплатно! «Исследователь» — это ваш первый шаг в мир, где блокировки исчезают, как дым. Скачай приложение, настрой за минуту и убедись, что анонимность — это просто. Начни свое путешествие сегодня!")
description_1 = (
    "1 месяц — Быстрый старт 🚀\n\n"
    "Погрузись в мир свободы интернета! «Быстрый старт» — идеальный вариант для тех, кто хочет попробовать всё и сразу. Быстрая настройка, мгновенный доступ и полное отсутствие ограничений. Всё это — за минимальную стоимость. Начни своё приключение прямо сейчас!")
description_2 = (
    "3 месяца — Безопасная Троица 🔐\n\n"
    "Три месяца уверенности и спокойствия. «Безопасная Троица» защитит тебя и твои данные, оставляя злых интернет-колдунов в стороне. Низкая стоимость, максимум удобства и полное отсутствие блокировок — всё это в одном пакете.")
description_3 = (
    "6 месяцев — Мастер Обфускации 🌀\n\n"
    "Полгода непревзойденной анонимности. «Мастер обфускации» виртуозно маскирует твой трафик, превращая его в загадку даже для самых настойчивых. Легко, доступно и надежно — для тех, кто ценит свободу!")
description_4 = (
    "12 месяцев — Элитный страж 🛡\n\n"
    "Целый год защиты и свободы в интернете. «Элитный страж» стоит на страже вашей анонимности, обеспечивая высший уровень безопасности. Забудьте про блокировки и наслаждайтесь стабильностью — всё это за лучшую цену.")

async def default_plans():
    async with async_session() as session:
        session.add(Plan(name="Исследователь (Бесплатно)", duration = 1, price=0, description=description_0))
        session.add(Plan(name="1 Месяц", duration = 1, price=1.56, description=description_1))
        session.add(Plan(name="3 Месяца", duration = 3, price=3.276, description=description_2))
        session.add(Plan(name="6 Месяцев", duration = 6, price=4.68, description=description_3))
        session.add(Plan(name="12 Месяцев", duration = 12, price=7.489, description=description_4))
        
        await session.commit()

