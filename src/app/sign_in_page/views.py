from django.shortcuts import render
import json
from databases.mysql_db import client_mysqldb
from PoW.generate_random_string import generate_random_string
from django.http import JsonResponse
import datetime

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

from Configs.Schemas.sign_in import SIGN_IN_PAGE_SCHEMA, SIGN_IN_SCHEMA
from Configs.Exceptions import NotFoundCookieIntoPowTable


@extend_schema(**SIGN_IN_PAGE_SCHEMA)
@api_view(['GET'])
def request_on_sign_in_page(requests):
    """
    Функция нужна для отправки страницы входа в систему

    :param requests:
    :return: render(requests, 'sign_in_page.html')
    """
    response = render(requests, 'sign_in_page.html')
    cookie = generate_random_string(10)

    client_mysqldb.create_cookie_into_pow_table(cookie)
    response.set_cookie('auth_sessionid', cookie)

    return response


@extend_schema(**SIGN_IN_SCHEMA)
@api_view(['POST'])
def request_on_sign_in_account(request):
    """
    Функция производит механизм аутентификации и авторизации пользователя в системе

    :param request:
    :return: 403, ok, Неверный пароль или почта
    """
    json_data = json.loads(request.body)
    return sign_in_user_account(request, json_data, 'admin-pollster' in json_data['login'])


def sign_in_user_account(request, json_data: dict, admin: bool = False):
    try:
        login = json_data.get('login')
        password = json_data.get('password')

        assert 'auth_sessionid' in request.COOKIES

        cookie = request.COOKIES['auth_sessionid']
        cookie_for_admin = generate_random_string(25)

        pow = json_data.get('pow', '')
        pow_from_db = client_mysqldb.get_pow(cookie)

        if pow == '' or pow != pow_from_db:
            return JsonResponse({'response': 'Неправильный pow в теле запроса. Challenge POW не был пройден правильно.'}, status=400)

        password_from_db, id_of_user = client_mysqldb.get_user_password_and_id_of_user_from_table(login)
        _, id_of_super_user = client_mysqldb.get_user_password_and_id_of_user_from_table(login, admin=admin)

        if client_mysqldb.check_user_into_ban_users(id_of_user):
            return JsonResponse({'response': 'Пользователь заблокирован в системе.'}, status=423)

        assert password == password_from_db
        assert password_from_db is not None

        expired = datetime.datetime.now()
        expired = expired + datetime.timedelta(days=20)

        response = JsonResponse({'response': 'Пользователь успешно авторизован в системе.'})

        if client_mysqldb.check_availability_entry_in_sessions(id_of_user):
            client_mysqldb.update_cookie_in_session_table(cookie, id_of_user, 'auth_sessionid', expired)
            if admin:
                client_mysqldb.update_cookie_in_session_table(cookie_for_admin, id_of_super_user, 'auth_admin_sessionid', expired)

        else:
            client_mysqldb.create_entry_into_sessions_table(cookie, 'auth_sessionid', id_of_user)
            if admin:
                client_mysqldb.create_entry_into_sessions_table(cookie_for_admin, 'auth_admin_sessionid', id_of_super_user)

        if admin:
            response.set_cookie('auth_admin_sessionid', cookie_for_admin)

        return response
    except AssertionError:
        return JsonResponse({'response': 'Неверный пароль или почта.'}, status=401)
    except NotFoundCookieIntoPowTable:
        return JsonResponse({'response': 'Перезагрузите страницу'}, status=400)