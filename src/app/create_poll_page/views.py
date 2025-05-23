import base64
import json
import random

from generate_qr_code import generate_qr_code_of_link

import mysql.connector
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseForbidden
from databases.mysql_db import client_mysqldb
from app.create_poll_page.set_poll import set_poll
from Configs.Exceptions import TryToXSS

from authentication.check_user_on_auth import authentication

from Tools_for_rabbitmq.producer import producer
from Configs.Commands_For_RMQ import Commands

from Configs.Hosts import Hosts

from Configs.Poll import SizeOfImage, Poll

import pathlib

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

from Configs.Schemas.create_poll import CREATE_POLL_PAGE_SCHEMA, CREATE_POLL_SCHEMA


@extend_schema(**CREATE_POLL_PAGE_SCHEMA)
@api_view(['GET'])
@authentication()
def request_on_create_poll_page(requests, id_of_user: int = None):
    """
    Функция нужна для загрузки конструктора опроса
    :param requests:
    :param id_of_user: идентификатор пользователя
    :return: render(requests, 'create_poll_page.html', context={'user': user, 'tags': tags.items()})
    """
    nickname = client_mysqldb.get_user_nickname_from_table_with_cookie(requests.COOKIES['auth_sessionid'], 'auth_sessionid')

    user = {'id': id_of_user, 'username': nickname}
    tags = {1: 'развлечения',  2: 'наука',  3: 'животные',  4: 'кухня',  5: 'искусство',  6: 'дети',  7: 'музыка',  8: 'кино и сериалы',  9: 'путешествия',  10: 'игры',  11: 'мода и стиль',  12: 'здоровье',  13: 'образование'}
    return render(requests, 'create_poll_page.html', context={'user': user, 'tags': tags.items()})


@extend_schema(**CREATE_POLL_SCHEMA)
@api_view(['POST'])
@authentication()
def request_on_create_new_poll(request: HttpRequest, id_of_user: int = None):
    """
    Функция создает записи в БД и создает сущность "опрос" в системе. Также функция проверяет запрос на XSS атаку, а также несоответствие данных

    :param request:
    :param id_of_user: идентификатор пользователя
    :return: True, False, 403
    """
    json_data = json.loads(request.body)
    try:
        poll, list_of_questions, list_of_options, list_of_right_answers, list_right_text_answer = set_poll(json_data, id_of_user)
        if 'cover' in json_data:
            if (((len(json_data['cover']) * 3) // 4) // 1048576) > SizeOfImage.size_of_cover:
                return HttpResponseForbidden("слишком большой размер изображения")
        result, poll = client_mysqldb.create_pool(
            poll, list_of_questions, list_of_options, list_of_right_answers, list_right_text_answer
        )
        if result:
            return on_success_create_poll(json_data, poll, result)
        else:
            return JsonResponse({'response': 'Опрос не был создан.'}, status=500)
    except TryToXSS:
        return JsonResponse({"response": "Попытка XSS атаки"}, status=403)
    except AssertionError:
        return JsonResponse({'response': 'Неправильные входные данные.'}, status=400)
    except mysql.connector.errors.DataError:
        return JsonResponse({'response': 'Опрос не был создан.'}, status=500)


def on_success_create_poll(json_data: dict, poll: Poll, result: bool):
    try:
        save_cover(json_data, poll)
    except Exception as ex:
        pass
    producer.publish(Commands.get_vector_poll % poll.id_of_poll)
    response_data = {"response": 'Опрос был успешно создан.', 'id_of_poll': poll.id_of_poll}
    if json_data['private']:
        return save_private_poll(poll, response_data)
    else:
        return JsonResponse(response_data)


def save_random_cover(images, poll):
    random_image = random.choice(images)

    with open(random_image, 'rb') as file:
        client_mysqldb.add_cover_into_cover_of_polls(poll.id_of_poll, file.read())


def save_cover_by_user(json_data, poll):
    cover = base64.b64decode(json_data['cover'])
    client_mysqldb.add_cover_into_cover_of_polls(poll.id_of_poll, cover)


def save_cover_by_pick(images: list, poll, pick: int):
    image = images[pick]

    with open(image, 'rb') as file:
        client_mysqldb.add_cover_into_cover_of_polls(poll.id_of_poll, file.read())


def save_cover(json_data, poll):
    dir_img = pathlib.Path('app/default_poll_imgs/')
    images = [path for path in dir_img.iterdir()][::-1]
    if 'cover' in json_data:
        save_cover_by_user(json_data, poll)

    elif 'coverDefault' in json_data and json_data['coverDefault'] != 0:
        if len(images) <= int(json_data['coverDefault']) - 1:
            save_random_cover(images, poll)
        else:
            save_cover_by_pick(images, poll, int(json_data['coverDefault']) - 1)
    else:
        save_random_cover(images, poll)


def save_private_poll(poll, response_data):
    try:
        code = client_mysqldb.add_entry_into_private_polls(poll.id_of_poll)
        base_64_qr_code = generate_qr_code_of_link('http://%s/%s' % (Hosts.domain, code))

        response_data['qr_code'] = base_64_qr_code
        response_data['url'] = "http://%s/%s" % (Hosts.domain, code)

        return JsonResponse(response_data)
    except Exception as ex:
        raise mysql.connector.errors.DataError