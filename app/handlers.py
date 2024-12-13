#handlers.py

# from aiogram.fsm.state import StatesGroup, State
# from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from config import ADMIN_ID
from app.utils import bill_url, qr_generator, generate_bill_id, payment_validation, calculate_end_date
import app.database.requests as rq

router = Router()

description_menu = (
    "🎉 <b>Приветствуем тебя, герой свободного интернета!</b>\n"
    "Ты оказался в правильном месте. Что будем делать дальше?\n\n"
    "1️⃣ <b>Посмотреть тарифы</b> — выбирай свой суперпакет и становись мастером обхода блокировок. Безопасность ждёт! 🕶️\n"
    "2️⃣ <b>Инфо</b> — загляни сюда, чтобы узнать, как долго твой щит анонимности будет на страже. 🛡\n\n"
    "📢 <b>Кстати!</b>\n"
    "У нас есть <a href=\"#\">телеграм-канал</a> с крутыми новостями и <a href=\"#\">чат техподдержки</a>, где тебя поймут, выслушают и помогут. Захочешь — заглядывай!"
)

# Оттвен на команду /start
@router.message(CommandStart() or F.data == ('main'))
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
    await message.reply(description_menu, reply_markup=kb.main, parse_mode="HTML")

# Главное меню
@router.callback_query(F.data == ('main'))
async def cmd_main(callback: CallbackQuery):
    await callback.answer('')
    
    await callback.message.answer(description_menu, reply_markup=kb.main, parse_mode="HTML")

# Инфо
@router.callback_query(F.data == ('info'))
async def cmd_info(callback: CallbackQuery):

    user_id = callback.from_user.id
    active_subscriptions = await rq.get_active_subscriptions(user_id)
    
    if active_subscriptions:
        
        table_rows = ""
        for subscription in active_subscriptions:
            table_rows += f"Название: {subscription.plan}\nПродолжительность: {subscription.duration} Мес.\nДата приобретения: {subscription.issue_date}\n\n"

        final_end_date = await calculate_end_date(active_subscriptions)
        
        subscription_message = f"Ваши подписки:\n\n{table_rows}Срок истечения всех подписок: {final_end_date}"

    else:
        subscription_message = "У вас нет Активных подписок. Самое время выбрать одино из наших классных предложений!"

    
    await callback.answer('')
    await callback.message.answer(subscription_message, reply_markup=kb.main, parse_mode="Markdown")


# /default
@router.message(Command('default'))
async def cmd_default(message: Message):
    if message.from_user.id == ADMIN_ID:
        await rq.default_plans()
        await message.reply('База данных заполнена')

# Показываем Планы подписки
@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('')
    tariff_description = (
        "🌍 <b>Добро пожаловать в мир свободного интернета!</b> Мы заботимся о вашей анонимности, доступности и безопасности. "
        "Выбирайте тариф, который подходит именно вам, и забудьте про блокировки, DPI и другие преграды. Всё, что нужно для свободы, — уже здесь!\n\n"
        
        "<b>1. 1 месяц — Исследователь 🧭</b>\n"
        "Пробуй интернет без границ бесплатно! \"Исследователь\" — это ваш первый шаг в мир, где блокировки исчезают, как дым. "
        "Скачай приложение, настрой за минуту и убедись, что анонимность — это просто. Начни своё путешествие сегодня!\n"
        "<b>Цена:</b> Бесплатно\n\n"
        
        "<b>2. 3 месяца — Безопасная Троица 🔐</b>\n"
        "Три месяца уверенности и спокойствия. \"Безопасная Троица\" защитит тебя и твои данные, оставляя злых интернет-колдунов в стороне. "
        "Низкая стоимость, максимум удобства и полное отсутствие блокировок — всё это в одном пакете.\n"
        "<b>Цена:</b> 2 Ton\n\n"
        
        "<b>3. 6 месяцев — Мастер Обфускации 🌀</b>\n"
        "Полгода непревзойденной анонимности. \"Мастер обфускации\" виртуозно маскирует твой трафик, превращая его в загадку даже для самых настойчивых. "
        "Легко, доступно и надежно — для тех, кто ценит свободу!\n"
        "<b>Цена:</b> 4 Ton\n\n"
        
        "<b>4. 12 месяцев — Элитный Страж 🛡</b>\n"
        "Целый год защиты и свободы в интернете. \"Элитный Страж\" стоит на страже вашей анонимности, обеспечивая высший уровень безопасности. "
        "Забудьте про блокировки и наслаждайтесь стабильностью — всё это за лучшую цену.\n"
        "<b>Цена:</b> 7 Ton"
    )

    await callback.message.answer(tariff_description, reply_markup=await kb.inline_buttons(), parse_mode="HTML")

# Полное Описание Планы подписки
@router.callback_query(F.data.startswith('plan_'))
async def category(callback: CallbackQuery):
    plan_data =  await rq.get_plan(callback.data.split('_')[1])

    if plan_data.price > 0:
        await callback.answer('')
        await callback.message.answer(plan_data.description, reply_markup=await kb.description_plans(callback.data.split('_')[1]))
    else:
        await callback.answer('')
        await callback.message.answer(plan_data.description, reply_markup=await kb.free_activate(callback.data.split('_')[1]))

# Высавление счета на оплату
@router.callback_query(F.data.startswith('pay_'))
async def pay_plan_one(callback: CallbackQuery):
    plan_data =  await rq.get_plan(callback.data.split('_')[1])
    user_id = callback.from_user.id
    bill_number = generate_bill_id()
    status = False
    plan = plan_data.name
    price = int(plan_data.price)
    duration = plan_data.duration

    if price >= 1:
        link = bill_url(price, bill_number)
        await rq.add_bill(user_id, bill_number, status, plan, price, link)
        input_file = qr_generator(link)
        
        invoice = (
            "⏳ <b>Ожидает оплату!</b>\n\n"
            f"Номер счёта: <b>{bill_number}</b>\n"
            f"Тариф: <b>{plan}</b>\n"
            f"Цена: <b>{price} Ton</b>\n"
            f"Срок действия: <b>{duration} месяца(ев)</b>\n\n"
            "После совершения платежа подождите пару минут, затем нажмите «Проверить оплату». 🕒\n\n"
            "Оплатить можно через кошелёк <b>Wallet</b> в Телеграм или <b>Tonkeeper</b>. Выберите удобный способ:\n\n"
            "👉 <a href='https://t.me/wallet'>Wallet в Телеграм</a>\n"
            "👉 <a href='https://tonkeeper.com'>Tonkeeper</a>\n\n"
            "Если возникнут вопросы или проблемы, не переживай — мы всегда рядом! Обращайся в наш чат техподдержки <a href='https://t.me/simply_network_support'>тут</a> 🔧💬"
        )

        await callback.answer('')
        await callback.message.answer_photo(caption=invoice, photo=input_file, reply_markup=await kb.check_pay(callback.data.split('_')[1], bill_number), parse_mode="HTML")
    
    if price == 0:
        if await rq.check_free_bill_exists(user_id) == False:
            await rq.add_bill(user_id, bill_number, status, plan, price, None)
            
            success_message = (
                "✅ <b>Отлично! Ты официально под защитой!</b>\n"
                "✨ <b>Ура! Пробный период активирован!</b> Испытай, каково это быть невидимым и свободным в сети. Пусть злые колдуны отдыхают! 🕶️\n\n"
                "🧾 <b>Детали оплаты:</b>\n"
                f"- Чек: <code>{bill_number}</code>\n"
                f"- Тариф: <b>{plan}</b>\n"
                f"- Цена: <b>{price} TON</b>\n"
                f"- Срок действия: <b>{duration} мес.</b>\n\n"
                "📌 <b>Что дальше?</b>\n"
                "Смело отправляйся в интернет-приключения, но если вдруг тёмные интернет-колдуны попробуют навредить, мы на страже! "
                "Задай вопросы или получи помощь в нашем <a href='https://t.me/simply_network_support'>чате техподдержки</a>.\n\n"
                "💪 Спасибо, что выбрал нас!"
            )

            await rq.update_bill_status(bill_number, True)
            await rq.set_subscription(user_id, bill_number, plan, duration, "Бесплатно")
            await callback.answer('Успешно')
            await callback.message.answer(success_message, parse_mode="HTML", reply_markup=kb.main)
        else:

            check = (
                "⚠️ <b>Пробный период уже активирован!</b>\n"
                "Не переживай, ты не пропустил момент. 🤔 Теперь время выбрать один из наших крутых тарифных планов и продолжить своё путешествие в мир анонимности и безопасности! 🚀🔒"
            )

            await callback.answer('')
            await callback.message.answer(check, reply_markup=await kb.inline_buttons(), parse_mode="HTML")

# Проверка оплаты в блокчейне
@router.callback_query(F.data.startswith('check_pay_'))
async def check_pay(callback: CallbackQuery):
    plan_data =  await rq.get_plan(callback.data.split('_')[2])
    
    bill_number = callback.data.split('_')[3]
    price = int(plan_data.price)
    
    validation = payment_validation(bill_number, price)

    if validation is not False:
        await rq.update_bill_status(bill_number, True)
        bot = callback.message.bot

        user_id = callback.from_user.id
        plan = plan_data.name
        duration = plan_data.duration

        username = callback.from_user.username
        first_name = callback.from_user.first_name
        last_name = callback.from_user.last_name

        admin_message = (
            f"Пользователь: <b>@{username}</b>\n"
            f"UserID: <code>{user_id}</code>\n"
            f"Имя: {first_name}\n"
            f"Фамилия: {last_name}\n\n"
            f"<b>Совершил платёж.</b>\n"
            f"Номер счёта: <code>{bill_number}</code>\n"
            f"План подписки: <b>{plan}</b>\n"
            f"Цена: <b>{price} Ton</b>\n"
            f"Срок действия: <b>{duration} мес.</b>\n\n"
            "<b>Требуется модерация.</b>"
        )

        success_message = (
            "✅ <b>Отлично! Ты официально под защитой!</b>\n\n"
            "✨ <b>Оплата прошла успешно.</b> Теперь ты член элитного клуба анонимных интернет-героев! 🎉\n\n"
            "🧾 <b>Детали оплаты:</b>\n"
            f"- Чек: <code>{bill_number}</code>\n"
            f"- Тариф: <b>{plan}</b>\n"
            f"- Цена: <b>{price} TON</b>\n"
            f"- Срок действия: <b>{duration} мес.</b>\n\n"
            "📌 <b>Что дальше?</b>\n"
            "Смело отправляйся в интернет-приключения, но если вдруг тёмные интернет-колдуны попробуют навредить, мы на страже! "
            "Задай вопросы или получи помощь в нашем <a href='https://t.me/simply_network_support'>чате техподдержки</a>.\n\n"
            "💪 Спасибо, что выбрал нас!"
        )

        await rq.set_subscription(user_id, bill_number, plan, duration, str(validation))
        await callback.answer('Успешно')
        await callback.message.edit_caption(caption=success_message, parse_mode="HTML")
        await bot.send_message(chat_id=ADMIN_ID, text=admin_message, reply_markup=kb.admin_check_point, parse_mode="HTML")
        
    else: 
        await callback.answer(f'Платеж еще не поступил! Возможно блокчейн перегружен. Такое иногда бывает, подождите пару минут и повторите попытку', show_alert=True)
