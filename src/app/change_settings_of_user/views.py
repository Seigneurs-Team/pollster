import datetime
import json
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseForbidden, JsonResponse

from authentication.check_user_on_auth import authentication
from databases.mysql_db import client_mysqldb


@authentication
def request_on_change_the_nickname(request: WSGIRequest, id_of_user: int = None):
    json_data = json.loads(request.body)
    assert 'nickname' in json_data

    client_mysqldb.update_the_filed_into_user(id_of_user, 'nickname', json_data['nickname'])
    return JsonResponse({'response': 200})


@authentication
def request_on_change_the_login(request: WSGIRequest, id_of_user: int = None):
    json_data = json.loads(request.body)
    assert 'email' in json_data

    client_mysqldb.update_the_filed_into_user(id_of_user, 'login', json_data['email'])


@authentication
def request_on_change_the_number_of_phone(request: WSGIRequest, id_of_user: int = None):
    json_data = json.loads(request.body)
    assert 'number_of_phone' in json_data

    client_mysqldb.update_the_filed_into_user(id_of_user, 'number_of_phone', json_data['number_of_phone'])
    return JsonResponse({'response': 200})


@authentication
def request_on_change_the_date_of_birth(request: WSGIRequest, id_of_user: int = None):
    json_data = json.loads(request.body)
    assert 'date_of_birth' in json_data

    try:
        date_of_birth = datetime.datetime.strptime(json_data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError:
        return HttpResponseForbidden("Некорректные данные")

    client_mysqldb.update_the_filed_into_user(id_of_user, 'date_of_birth', date_of_birth)
    return JsonResponse({'response': 200})


@authentication
def request_on_change_the_tags(request: WSGIRequest, id_of_user: int = None):
    json_data = json.loads(request.body)

    assert 'tags_of_user' in json_data
    assert isinstance(json_data['tags_of_user'], list)
    assert len(json_data['tags_of_user']) <= 4

    client_mysqldb.update_the_filed_into_user(id_of_user, 'tags', json.dumps(json_data['tags_of_user'], ensure_ascii=False))
    return JsonResponse({'response': 200})


