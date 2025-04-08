import datetime
import json
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseForbidden, JsonResponse

from authentication.check_user_on_auth import authentication_for_change_user_data
from databases.mysql_db import client_mysqldb

from Tools_for_rabbitmq.producer import producer
from Configs.Commands_For_RMQ import Commands


@authentication_for_change_user_data
def request_on_change_the_nickname(request: WSGIRequest, id_of_user: int = None):
    """
    Функция нужна для обработки запроса изменения никнейма пользователя
    :param request:
    :param id_of_user: идентификатор пользователя
    :return: 403 или 200
    """
    json_data = json.loads(request.body)
    if 'nickname' not in json_data:
        return HttpResponseForbidden("Некорректные данные")

    client_mysqldb.update_the_filed_into_user(id_of_user, 'nickname', json_data['nickname'])
    return JsonResponse({'response': 200})


@authentication_for_change_user_data
def request_on_change_the_login(request: WSGIRequest, id_of_user: int = None):
    """
    Функция нужна для изменения логина пользователя
    :param request:
    :param id_of_user: идентификатор пользователя
    :return: 200 или 403
    """
    json_data = json.loads(request.body)
    if 'email' not in json_data:
        return HttpResponseForbidden("Некорректные данные")

    client_mysqldb.update_the_filed_into_user(id_of_user, 'login', json_data['email'])
    return JsonResponse({'response': 200})


@authentication_for_change_user_data
def request_on_change_the_number_of_phone(request: WSGIRequest, id_of_user: int = None):
    """
    Функция нужна для изменения номера телефона пользователя
    :param request:
    :param id_of_user: идентификатор пользователя
    :return: 403 или 200
    """
    json_data = json.loads(request.body)
    if 'number_of_phone' not in json_data:
        return HttpResponseForbidden("Некорректные данные")

    client_mysqldb.update_the_filed_into_user(id_of_user, 'number_of_phone', json_data['number_of_phone'])
    return JsonResponse({'response': 200})


@authentication_for_change_user_data
def request_on_change_the_date_of_birth(request: WSGIRequest, id_of_user: int = None):
    """
    Функция нужна для изменения даты дня рождения пользователя
    :param request:
    :param id_of_user: идентификатор пользователя
    :return: 403 или 200
    """
    json_data = json.loads(request.body)
    if 'date_of_birth' not in json_data:
        return HttpResponseForbidden("Некорректные данные")

    try:
        date_of_birth = datetime.datetime.strptime(json_data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError:
        return HttpResponseForbidden("Некорректные данные")

    client_mysqldb.update_the_filed_into_user(id_of_user, 'date_of_birth', date_of_birth)
    return JsonResponse({'response': 200})


@authentication_for_change_user_data
def request_on_change_the_tags(request: WSGIRequest, id_of_user: int = None):
    """
    Функция нужна для изменения списка тегов пользователя
    :param request:
    :param id_of_user: идентификатор пользователя
    :return: 403 или 200
    """
    json_data = json.loads(request.body)

    if ('tags_of_user' not in json_data)\
            or (isinstance(json_data['tags_of_user'], list) is False)\
            or (len(json_data['tags_of_user']) > 4):
        return HttpResponseForbidden("Некорректные данные")

    if len(json_data['tags_of_user']) != 0:
        client_mysqldb.update_the_filed_into_user(id_of_user, 'tags', json.dumps(json_data['tags_of_user'], ensure_ascii=False))
        producer.publish(Commands.get_vector_user % id_of_user)
    else:
        client_mysqldb.update_the_filed_into_user(id_of_user, 'tags', None)
    return JsonResponse({'response': 200})


