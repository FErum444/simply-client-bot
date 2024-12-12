# utils.py

import qrcode
from io import BytesIO
from config import MAIN_WALLET, THRESHOLD
from aiogram.types import BufferedInputFile
import requests
import uuid
from datetime import datetime
from dateutil.relativedelta import relativedelta

def convert_ton_to_nanoton(ton: float | int) -> int:
    nanoton = int(ton * 1e9)
    return nanoton

def bill_url(price, bill_number):
    price_nano = convert_ton_to_nanoton(price)
    wallet_url = "ton://transfer/" + MAIN_WALLET + "?amount=" + str(price_nano) + "&text=" + str(bill_number)
    return wallet_url

def qr_generator(link):
    qr = qrcode.QRCode(
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    bio = BytesIO()
    bio.name = 'qrcode.png'
    img.save(bio)
    bio.seek(0)

    input_file = BufferedInputFile(bio.read(), filename="qrcode.png")
    
    return input_file

def generate_bill_id(length: int = 12) -> str:

    if length <= 0 or length > 32:
        raise ValueError("Length must be between 1 and 32.")
    return uuid.uuid4().hex[:length]


def balance_response(main_address, limit='10'):
    params = {
        'address': main_address,
        'limit': limit
    }

    response = requests.get('https://api.tonscan.com/api/bt/getTransactionsForAddress', params=params)
    return response.json()


def find_dict_with_key_value(data, target_key, target_value):

    results = []

    if isinstance(data, dict):
        # Если текущий словарь содержит нужный ключ и значение
        if target_key in data and data[target_key] == target_value:
            results.append(data)
        # Рекурсивно проверяем вложенные структуры
        for value in data.values():
            if isinstance(value, (dict, list)):
                results.extend(find_dict_with_key_value(value, target_key, target_value))

    elif isinstance(data, list):
        # Проверяем каждый элемент списка
        for item in data:
            if isinstance(item, (dict, list)):
                results.extend(find_dict_with_key_value(item, target_key, target_value))

    return results


def payment_validation(bill_number, price): # bill_number, price
    data = balance_response(MAIN_WALLET)
    result = find_dict_with_key_value(data, target_key = "message", target_value = bill_number)

    price = convert_ton_to_nanoton(price)
    threshold = THRESHOLD

    for item in result:
        if item.get("message") == bill_number and item.get("op") == "0x0" and item.get("destination") == MAIN_WALLET:
            variable_2 = item.get("value")
            difference = abs(price - variable_2) / price * 100

            # Проверка превышения порога
            if difference <= threshold:
                # print(f"Элемент: {item}")
                # print(f"Отклонение {difference:.5f}% не превышает порог {threshold}%.\n")
                return item
            else:
                # print(f"Элемент: {item}")
                # print(f"Отклонение {difference:.5f}% превышает порог {threshold}%.\n")
                return False
        return False
    return False

async def calculate_end_date(active_subscriptions):
    if not active_subscriptions:
        return None

    sorted_subscriptions = sorted(active_subscriptions, key=lambda sub: sub.issue_date)
    start_date = datetime.strptime(sorted_subscriptions[0].issue_date, "%Y-%m-%d %H:%M:%S")

    end_date = start_date

    for subscription in sorted_subscriptions:
        duration_months = subscription.duration
        end_date += relativedelta(months=duration_months)

    return end_date.strftime("%Y-%m-%d %H:%M:%S")