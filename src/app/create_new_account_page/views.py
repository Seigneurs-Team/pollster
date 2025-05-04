from django.shortcuts import render
import json
from PoW.generate_random_string import generate_random_string
from databases.mysql_db import client_mysqldb
from Configs.Exceptions import ErrorSameLogins, NotFoundCookieIntoPowTable
from django.http import JsonResponse

from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Configs.Schemas.create_new_account import CREATE_NEW_ACCOUNT_PAGE_SCHEMA, CREATE_NEW_ACCOUNT_SCHEMA


@extend_schema(**CREATE_NEW_ACCOUNT_PAGE_SCHEMA)
@api_view(['GET'])
def request_on_create_new_account_page(requests):
    """
    Функция возвращает страницу создания нового аккаунта
    :param requests:
    :return: render(requests, 'create_new_account_page.html')
    """
    response = render(requests, 'create_new_account_page.html')
    cookie = generate_random_string(10)

    client_mysqldb.create_cookie_into_pow_table(cookie)
    response.set_cookie('auth_sessionid', cookie)
    return response


@extend_schema(**CREATE_NEW_ACCOUNT_SCHEMA)
@api_view(['POST'])
def request_on_create_new_account(request):
    """
    Функция нужна для успешного создания нового аккаунта на основе тех данных, которые передаются в JSON запроса

    :param request:
    :return: 200, либо коды ошибок (1, 2, 3)
    """
    try:
        json_data = json.loads(request.body)
        login = json_data.get('login')
        password = json_data.get('password')
        pow = json_data.get('pow', '')
        nickname = json_data.get('nickname', '')

        assert pow != ''
        assert 'auth_sessionid' in request.COOKIES

        cookie = request.COOKIES['auth_sessionid']

        pow_from_db = client_mysqldb.get_pow(cookie)

        assert pow == pow_from_db

        client_mysqldb.create_user(login, password, 1, nickname)
        client_mysqldb.delete_pow_entry_from_pow_table(cookie)

        _, id_of_user = client_mysqldb.get_user_password_and_id_of_user_from_table(login)
        client_mysqldb.create_entry_into_sessions_table(cookie, 'auth_sessionid', id_of_user)

        return JsonResponse({'response': 'Пользователь был успешно создан.'})
    except AssertionError:
        return JsonResponse({'error_code': 1, 'message': 'Не найдено значение pow в запросе либо не найден куки файл.'}, status=400)
    except ErrorSameLogins:
        return JsonResponse({'error_code': 2, 'message': 'Данный логин уже занят.'}, status=409)
    except NotFoundCookieIntoPowTable:
        return JsonResponse({'error_code': 3, 'message': 'Недействительный куки'}, status=401)