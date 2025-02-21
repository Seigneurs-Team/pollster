from django.shortcuts import render
import json
from PoW.generate_random_string import generate_random_string
from databases.mysql_db import client_mysqldb
from django.http import JsonResponse


def request_on_create_new_account_page(requests):
    print('rendering create_new_account_page...')
    response = render(requests, 'create_new_account_page.html')
    cookie = generate_random_string(10)

    client_mysqldb.create_cookie_into_pow_table(cookie)
    response.set_cookie('auth_sessionid', cookie)
    return response


def request_on_create_new_account(request):
    try:
        json_data = json.loads(request.body)
        login = json_data.get('login')
        password = json_data.get('password')
        pow = json_data.get('pow', '')
        nickname = json_data.get('nickname')

        assert pow != ''
        assert 'auth_sessionid' in request.COOKIES

        cookie = request.COOKIES['auth_sessionid']

        pow_from_db = client_mysqldb.get_pow(cookie)

        assert pow == pow_from_db

        client_mysqldb.create_user(login, password, 'user', nickname)

        return JsonResponse({'response': 'ok'})
    except AssertionError:
        return JsonResponse({'response': 'not ok'})
