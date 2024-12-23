import requests
import json
import uuid
import time
import os
from config import ADMIN_USERNAME, ADMIN_PASSWORD, BASE_WEBHOOK_URL, TOKEN_FILE

def get_token():
    """
    Получение нового токена с API.
    """
    API_URL = BASE_WEBHOOK_URL + "/api/admin/token"
    payload = {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD,
        'grant_type': 'password'
    }

    try:
        response = requests.post(API_URL, data=payload, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        if not all(key in token_data for key in ["access_token", "token_type"]):
            raise ValueError("Ответ сервера не содержит ожидаемых ключей: access_token, token_type")

        token_data['timestamp'] = time.time()
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f)

        return token_data

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ошибка при запросе токена: {e}")
    except (ValueError, KeyError) as e:
        raise RuntimeError(f"Некорректный формат данных токена: {e}")

def get_valid_token():
    """
    Возвращает валидный токен из файла или запрашивает новый.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)

            if not all(key in token_data for key in ["access_token", "token_type", "timestamp"]):
                raise ValueError("Файл токена не содержит необходимых ключей")

            if time.time() - token_data['timestamp'] < 86400:
                return token_data
            else:
                return get_token()

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Ошибка чтения токена из файла: {e}. Запрашиваем новый токен.")
            return get_token()

    else:
        return get_token()

def make_request():
    """
    Возвращает данные токена и заголовки авторизации.
    """
    token_data = get_valid_token()
    headers = {
        'Authorization': f"Bearer {token_data['access_token']}"
    }
    return token_data, headers

def add_new_user(username, token_data):
    """
    Добавление нового пользователя через API.
    """
    url = BASE_WEBHOOK_URL + "/api/user"
    
    payload = {
        "proxies": {
            "vless": {
                "id": str(uuid.uuid4()),
                "flow": "xtls-rprx-vision"
            }
        },
        "expire": None,
        "data_limit": None,
        "data_limit_reset_strategy": "no_reset",
        "inbounds": {
            "vless": ["VLESS TCP REALITY"]
        },
        "note": "",
        "sub_updated_at": None,
        "sub_last_user_agent": None,
        "online_at": None,
        "on_hold_expire_duration": None,
        "on_hold_timeout": None,
        "auto_delete_in_days": None,
        "username": username,
        "status": "active",
        "used_traffic": 0,
        "lifetime_used_traffic": 0,
        "created_at": ""
    }

    try:
        json_payload = json.dumps(payload)
        headers = {
            'Authorization': f"Bearer {token_data['access_token']}",
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=json_payload, timeout=10)
        response.raise_for_status()
        # print(response.text)
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при добавлении пользователя: {e}")

def check_user_exists(username, token_data):
    """
    Проверяет, существует ли пользователь на сервере.
    """
    url = BASE_WEBHOOK_URL + f"/api/user/{username}"
    
    try:
        headers = {
            'Authorization': f"Bearer {token_data['access_token']}"
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("Пользователь найден:", response.json())
            return True
        elif response.status_code == 404:
            print("Пользователь не найден.")
            return False
        else:
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False

def modify_user(username, token_data, **kwargs):
    """
    Изменяет параметры существующего пользователя.
    
    :param username: Имя пользователя
    :param token_data: Токен авторизации
    :param kwargs: Параметры для изменения, например status, expire, data_limit и т.д.
    """
    url = BASE_WEBHOOK_URL + f"/api/user/{username}"

    try:
        headers = {
            'Authorization': f"Bearer {token_data['access_token']}",
            'Content-Type': 'application/json'
        }

        payload = {key: value for key, value in kwargs.items() if value is not None}

        if not payload:
            raise ValueError("Не указаны параметры для изменения пользователя.")

        response = requests.put(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()

        # print("Пользователь успешно изменен:", response.json())
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при изменении пользователя: {e}")
    except ValueError as e:
        print(f"Ошибка в параметрах: {e}")

# Упрощённый интерфейс для импорта
__all__ = [
    "get_token",
    "get_valid_token",
    "make_request",
    "add_new_user",
    "check_user_exists",
    "modify_user"
]
