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
from app.services import make_request, check_user_exists, add_new_user, modify_user, get_user

router = Router()

description_menu = (
    "🎉 <b>Приветствуем тебя, герой свободного интернета!</b>\n"
    "Ты оказался в правильном месте. Что будем делать дальше?\n\n"
    "1️⃣ <b>Посмотреть тарифы</b> — выбирай свой суперпакет и становись мастером обхода блокировок. Безопасность ждёт! 🕶️\n"
    "2️⃣ <b>Инфо</b> — загляни сюда, чтобы узнать, как долго твой щит анонимности будет на страже. 🛡\n\n"
    "📢 <b>Кстати!</b>\n"
    "У нас есть <a href='https://t.me/Simply_Network'>телеграм-канал</a> с крутыми новостями и <a href='https://t.me/simply_network_support'>чат техподдержки</a>, где тебя поймут, выслушают и помогут. Захочешь — заглядывай!"
)

# Ответ на команду /start
@router.message(CommandStart() or F.data == ('main'))
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
    await message.answer(description_menu, reply_markup=kb.main, parse_mode="HTML")

# Главное меню
@router.callback_query(F.data == ('main'))
async def cmd_main(callback: CallbackQuery):
    await callback.answer('')
    
    await callback.message.edit_text(description_menu, reply_markup=kb.main, parse_mode="HTML")

# Инфо
@router.callback_query(F.data == ('info'))
async def cmd_info(callback: CallbackQuery):

    user_id = callback.from_user.id
    active_subscriptions = await rq.get_active_subscriptions(user_id)


    token_data, headers = make_request()
    user_vpn_data = get_user(user_id, token_data)
    
    links = user_vpn_data.get('links', [])
    
    if active_subscriptions:
        
        table_rows = ""
        for subscription in active_subscriptions:
            table_rows += f"<b>Продолжительность:</b> {subscription.plan}\n<b>Дата приобретения:</b> {subscription.issue_date}\n\n"

        final_end_date = await calculate_end_date(active_subscriptions)
        
        subscription_message = f"<b>Ваши подписки:</b>\n\n{table_rows}<b>Срок истечения всех подписок:</b> {final_end_date}\n\n<code>{links[0]}</code>"

    else:
        subscription_message = "У вас нет Активных подписок. Самое время выбрать одино из наших классных предложений!"

    
    await callback.answer('')
    await callback.message.edit_text(subscription_message, reply_markup=kb.main, parse_mode="HTML")


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
    
    "<b>1 месяц — Исследователь 🧭</b>\n"
    "Пробуй интернет без границ бесплатно! «Исследователь» — это ваш первый шаг в мир, где блокировки исчезают, как дым. "
    "Скачай приложение, настрой за минуту и убедись, что анонимность — это просто. Начни своё путешествие сегодня!\n\n"
    "<b>Цена:</b> Бесплатно 🎁✨\n\n\n"
    
    "<b>1 месяц — Быстрый старт 🚀</b>\n"
    "Погрузись в мир свободы интернета! «Быстрый старт» — идеальный вариант для тех, кто хочет попробовать всё и сразу. "
    "Быстрая настройка, мгновенный доступ и полное отсутствие ограничений. Всё это — за минимальную стоимость. "
    "Начни своё приключение прямо сейчас!\n\n"
    "<b>Цена:</b> 1.56 Ton 💎 (~1000₽ в месяц 💰)\n\n\n"
    
    "<b>3 месяца — Безопасная Троица 🔐</b>\n"
    "Три месяца уверенности и спокойствия. «Безопасная Троица» защитит тебя и твои данные, оставляя злых интернет-колдунов в стороне. "
    "Низкая стоимость, максимум удобства и полное отсутствие блокировок — всё это в одном пакете.\n\n"
    "<b>Цена:</b> 3.276 Ton 💎 (~700₽ в месяц 💰) на 30% 🏷️ Дешевле\n\n\n"
    
    "<b>6 месяцев — Мастер Обфускации 🌀</b>\n"
    "Полгода непревзойденной анонимности. «Мастер обфускации» виртуозно маскирует твой трафик, превращая его в загадку даже для самых настойчивых. "
    "Легко, доступно и надежно — для тех, кто ценит свободу!\n\n"
    "<b>Цена:</b> 4.68 Ton 💎 (~500₽ в месяц 💰) на 50% 🏷️ Дешевле\n\n\n"
    
    "<b>12 месяцев — Элитный Страж 🏆</b>\n"
    "Целый год защиты и свободы в интернете. «Элитный Страж» стоит на страже вашей анонимности, обеспечивая высший уровень безопасности. "
    "Забудьте про блокировки и наслаждайтесь стабильностью — всё это за лучшую цену.\n\n"
    "<b>Цена:</b> 7.489 Ton 💎 (~400₽ в месяц 🌟) на 60% 🏷️ Дешевле"
)

    await callback.message.edit_text(tariff_description, reply_markup=await kb.inline_buttons(), parse_mode="HTML")

# Полное Описание Планы подписки
@router.callback_query(F.data.startswith('plan_'))
async def category(callback: CallbackQuery):
    plan_data =  await rq.get_plan(callback.data.split('_')[1])

    if plan_data.price > 0:
        await callback.answer('')
        await callback.message.edit_text(plan_data.description, reply_markup=await kb.description_plans(callback.data.split('_')[1]))
    else:
        await callback.answer('')
        await callback.message.edit_text(plan_data.description, reply_markup=await kb.free_activate(callback.data.split('_')[1]))

# Высавление счета на оплату
@router.callback_query(F.data.startswith('pay_'))
async def pay_plan_one(callback: CallbackQuery):
    plan_data =  await rq.get_plan(callback.data.split('_')[1])
    user_id = callback.from_user.id
    bill_number = generate_bill_id()
    status = False
    plan = plan_data.name
    price = float(plan_data.price)
    duration = plan_data.duration

    if price > 0.0001:
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

            # Получаем токен и заголовки
            token_data, headers = make_request()

            # Проверяем, существует ли пользователь
            if not check_user_exists(user_id, token_data):
                # Если пользователь не существует, создаём его
                user_vpn_data = add_new_user(user_id, token_data)
            else:
                # Если пользователь существует, обновляем его статус на active
                user_vpn_data = modify_user(user_id, token_data, status="active")
            
            links = user_vpn_data.get('links', [])

            
            success_message = (
                "✅ <b>Отлично! Ты официально под защитой!</b>\n\n"
                "✨ <b>Ура! Пробный период активирован!</b> Испытай, каково это быть невидимым и свободным в сети. Пусть злые колдуны отдыхают! 🕶️\n\n"
                "🧾 <b>Детали оплаты:</b>\n"
                f"- Чек: <code>{bill_number}</code>\n"
                f"- Тариф: <b>{plan}</b>\n"
                f"- Цена: <b>{price} TON</b>\n"
                f"- Срок действия: <b>{duration} мес.</b>\n\n"
                "📌 <b>Что дальше?</b>\n"
                "Смело отправляйся в интернет-приключения, но если вдруг тёмные интернет-колдуны попробуют навредить, мы на страже! "
                "Задай вопросы или получи помощь в нашем <a href='https://t.me/simply_network_support'>чате техподдержки</a>.\n\n"
                "💪 Спасибо, что выбрал нас!\n\n"
                f"<code>{links[0]}</code>"
            )

            await rq.update_bill_status(bill_number, True)
            await rq.set_subscription(user_id, bill_number, plan, duration, "Бесплатно")
            await callback.answer('Успешно')
            await callback.message.answer(success_message, parse_mode="HTML", reply_markup=kb.how_to_use)
        else:

            check = (
                "⚠️ <b>Пробный период уже активирован!</b>\n"
                "Не переживай, ты не пропустил момент. 🤔 Теперь время выбрать один из наших крутых тарифных планов и продолжить своё путешествие в мир анонимности и безопасности! 🚀🔒"
            )

            await callback.answer('')
            await callback.message.edit_text(check, reply_markup=await kb.inline_buttons(), parse_mode="HTML")

# Проверка оплаты в блокчейне
@router.callback_query(F.data.startswith('check_pay_'))
async def check_pay(callback: CallbackQuery):
    plan_data = await rq.get_plan(callback.data.split('_')[2])
    bill_number = callback.data.split('_')[3]
    
    price = float(plan_data.price)
    
    # Тестовая вализация
    # bill_number = "2d8c75ae3099"
    # price = 2.00

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

        # Получаем токен и заголовки
        token_data, headers = make_request()

        # Проверяем, существует ли пользователь
        if not check_user_exists(user_id, token_data):
            # Если пользователь не существует, создаём его
            user_vpn_data = add_new_user(user_id, token_data)
        else:
            # Если пользователь существует, обновляем его статус на active
            user_vpn_data = modify_user(user_id, token_data, status="active")
        
        links = user_vpn_data.get('links', [])

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
            f"<code>{links[0]}</code>"
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
            "💪 Спасибо, что выбрал нас!\n\n"
            f"<code>{links[0]}</code>"
        )

        await rq.set_subscription(user_id, bill_number, plan, duration, str(validation))
        await callback.answer('Успешно')
        await callback.message.edit_caption(caption=success_message, parse_mode="HTML", reply_markup=kb.how_to_use)
        await bot.send_message(chat_id=ADMIN_ID, text=admin_message, reply_markup=kb.admin_check_point, parse_mode="HTML")
        
    else: 
        await callback.answer(f'Платеж еще не поступил! Возможно блокчейн перегружен. Такое иногда бывает, подождите пару минут и повторите попытку', show_alert=True)


# Показываем Планы подписки
@router.callback_query(F.data == 'how_to_use')
async def how_to_use(callback: CallbackQuery):
    await callback.answer('')
    tariff_description = (
        "Как стать частью элиты анонимного интернета?\n\n"
        "1️⃣ Скачай приложение из  "
        "<a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>App Store</a>, "
        "<a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn'>Google Play</a> или с "
        "<a href='https://amnezia.org/ru/downloads'>официального сайта</a>. Мы дружим с "
        "<a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3.dmg'>Mac OS</a>, "
        "<a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>Windows</a> "
        "и даже <a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_Linux_installer.tar.zip'>Linux</a>. 🖥\n"
        "2️⃣ Открой приложение AmneziaVPN и нажми «Приступим».\n"
        "3️⃣ Вставляй сюда длинную ссылку, указанную в чеке или меню «Инфо».\n\n"
        "Вуаля! Ты уже серфишь по интернету безопасно и без страха. 🕶"
    )

    await callback.message.answer(tariff_description, reply_markup=kb.main, disable_web_page_preview=True, parse_mode="HTML")