
from app.services import make_request, add_new_user, check_user_exists, modify_user


token_data, headers = make_request()
username = '65778833'

# Заводим VPN польгователя
# add_new_user(username, token_data)

# Проверяем существование VPN польгователя
# test_result_1 = check_user_exists(username, token_data)
# print(test_result_1)


# Вызываем функцию для изменения параметров VPN пользователя "active" "disabled"
# params_to_modify = {"status": "active",}
# modify_user(username, token_data, **params_to_modify)
