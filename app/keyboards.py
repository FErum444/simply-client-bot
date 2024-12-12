# keyboards.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.database.requests import get_plans

# Главное Меню Инлайн
main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Цены', callback_data='catalog')], [InlineKeyboardButton(text='Инфо', callback_data='info')]
])

# Выбор Тарифа Инлайн (Новая)
async def inline_buttons():
    all_plans = await get_plans()
    keyboard = InlineKeyboardBuilder()
    for plan in all_plans: 
        keyboard.add(InlineKeyboardButton(text=plan.name, callback_data=f"plan_{plan.id}"))
    keyboard.add(InlineKeyboardButton(text="На Главную", callback_data="main"))
    return keyboard.adjust(2).as_markup()


# Меню Тарифа Инлайн
description = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Купить', callback_data='pay')], [InlineKeyboardButton(text='Назад', callback_data='catalog')]
])

# Меню Купить Инлайн
async def description_plans(id_plan):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Купить', callback_data=f'pay_{id_plan}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='catalog'))
    return keyboard.adjust(2).as_markup()

# Проверка оплаты
async def check_pay(id_plan, bill_number):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Проверить оплату', callback_data=f'check_pay_{id_plan}_{bill_number}'))
    return keyboard.adjust(2).as_markup()

# Активация Пробного Периода
async def free_activate(id_plan):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Активировать', callback_data=f'pay_{id_plan}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='catalog'))
    return keyboard.adjust(2).as_markup()

# Админская чекпойнт клавиатура (нигечго не делает)
admin_check_point = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить', url="https://globalsimply.ru:4444/dashboard/")]
])