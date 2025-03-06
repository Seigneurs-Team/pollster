from django.shortcuts import render
import json
from databases.mysql_db import client_mysqldb
from PoW.generate_random_string import generate_random_string
from django.http import JsonResponse
import datetime


def request_on_sign_in_page(requests):
    response = render(requests, 'sign_in_page.html')
    cookie = generate_random_string(10)

    client_mysqldb.create_cookie_into_pow_table(cookie)
    response.set_cookie('auth_sessionid', cookie)

    return response


def request_on_sign_in_account(request):
    try:
        json_data = json.loads(request.body)

        login = json_data.get('login')
        password = json_data.get('password')

        assert 'auth_sessionid' in request.COOKIES

        cookie = request.COOKIES['auth_sessionid']

        pow = json_data.get('pow', '')
        pow_from_db = client_mysqldb.get_pow(cookie)

        assert pow != ''
        assert pow == pow_from_db

        password_from_db, id_of_user = client_mysqldb.get_user_password_and_id_of_user_from_table(login)
        assert password == password_from_db

        expired = datetime.datetime.now()
        expired = expired + datetime.timedelta(days=3)

        client_mysqldb.update_cookie_in_session_table(cookie, id_of_user, 'auth_sessionid', expired)

        return JsonResponse({'response': 'ok'})
    except AssertionError:
        return JsonResponse({'response': 'not ok'})




