import base64
import json
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

from Configs.Poll import SizeOfImage


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
        result = client_mysqldb.create_pool(
            poll, list_of_questions, list_of_options, list_of_right_answers, list_right_text_answer
        )
        cover = base64.b64decode(json_data['cover'])
        client_mysqldb.add_cover_into_cover_of_polls(poll.id_of_poll, cover)
        if result:
            producer.publish(Commands.get_vector_poll % poll.id_of_poll)
        if json_data['private']:
            code = client_mysqldb.add_entry_into_private_polls(poll.id_of_poll)
            base_64_qr_code = generate_qr_code_of_link('http://%s/%s' % (Hosts.domain, code))
            return JsonResponse({"result": result, "qr_code": base_64_qr_code, "url": "http://%s/%s" % (Hosts.domain, code)})
        return JsonResponse({"result": result})
    except TryToXSS:
        return HttpResponseForbidden("Попытка XSS атаки")
    except AssertionError:
        return HttpResponseForbidden()
    except mysql.connector.errors.DataError:
        return HttpResponseForbidden("Ошибка базы данных")
