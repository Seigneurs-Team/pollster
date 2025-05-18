import typing

from django.shortcuts import render

from databases.mysql_db import client_mysqldb
from Configs.Exceptions import NotFoundPoll, RepeatPollError, TryToXSS
from authentication.check_user_on_auth import authentication_for_passing_poll_page, authentication

import json

from django.http import JsonResponse, HttpResponseForbidden

from Tools_for_rabbitmq.producer import producer
from log_system.Levels import Levels

from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Configs.Schemas.passing_poll import PASSING_POLL_PAGE_SCHEMA, PASSING_POLL_SCHEMA


@extend_schema(**PASSING_POLL_PAGE_SCHEMA)
@api_view(['GET'])
@authentication_for_passing_poll_page
def request_on_passing_poll_page(requests, poll_id: typing.Union[int, str], id_of_user: int = None):
    """
    Функция нужна для возврата страницы с прохождением конкретного опроса.
    Страница включает в себя все вопросы опроса, а также опции к этим опросам.

    :param requests:
    :param poll_id: идентификатор опроса
    :param id_of_user: идентификатор пользователя
    :return: render(requests, 'passing_poll_page.html', context={'user': user, 'poll': poll, 'is_pass': is_pass})
    или render(requests, 'NotFound.html')
    """
    producer.publish_log('Получил запрос на рендеринг страницы прохождения опроса', Levels.Debug, id_of_user, requests=requests)
    # получение опроса по id
    auth_sessionid = requests.COOKIES['auth_sessionid']
    nickname = client_mysqldb.get_user_nickname_from_table_with_cookie(auth_sessionid, 'auth_sessionid')
    is_pass = client_mysqldb.check_user_on_pass_the_poll(id_of_user, poll_id)

    user = {'id': id_of_user, 'username': nickname}
    try:
        poll = client_mysqldb.get_poll(poll_id)
        return render(requests, 'passing_poll_page.html', context={'user': user, 'poll': poll, 'is_pass': is_pass})
    except NotFoundPoll as _ex:
        return render(requests, 'NotFound.html')


@extend_schema(**PASSING_POLL_SCHEMA)
@api_view(['POST'])
@authentication()
def request_on_passing_poll(request, id_of_user: int = None):
    """
    Функция нужна для того, чтобы сохранить данные, которые пользователь ввел в ответах на вопросы в опросе.
    Сохраняется в БД идентификатор опроса, порядковый номер вопроса, тип вопроса и ответ на него, а также идентификатор
    пользователя

    :param request:
    :param id_of_user: идентификатор пользователя
    :return: 200, 403
    """
    data_of_passing_poll = json.loads(request.body)
    auth_sessionid = request.COOKIES['auth_sessionid']
    id_of_poll = data_of_passing_poll['poll_id']

    producer.publish_log(
        'Получил POST запрос с данными, который пользователь ввел в опросе',
        Levels.Info, id_of_user, request, other_data={'id_of_poll': id_of_poll})

    try:
        client_mysqldb.add_users_into_table_for_users_who_pass_the_poll(id_of_user, id_of_poll)

        producer.publish_log(
            'Начало сохранения ответов пользователя', Levels.Info,
            id_of_user, requests=request, other_data={'id_of_poll': id_of_poll, 'count_of_answers': len(data_of_passing_poll['answers'])}
        )

        client_mysqldb.save_answers_users_into_table_of_passing_poll_from_user(data_of_passing_poll['answers'], id_of_user, id_of_poll)
        producer.publish_log("Данные были успешно сохранены", Levels.Info, id_of_user, requests=request, other_data={'id_of_poll': id_of_poll})
    except RepeatPollError:
        return JsonResponse({'response': 'Вы уже прошли данный опрос.'}, status=403)
    except TryToXSS:
        producer.publish_log(
            'Была пресечена попытка XSS атаки', Levels.Warning,
            id_of_user, requests=request, other_data={'id_of_poll': id_of_poll}
        )
        client_mysqldb.delete_cookie_from_session_table(auth_sessionid, 'auth_sessionid', id_of_user)
        return JsonResponse({'response': 'Неправильные типы вопросов были отправлены на сервер.'}, status=400)
    else:
        return JsonResponse({'response': 'Данные были успешно сохранены в БД.'})
