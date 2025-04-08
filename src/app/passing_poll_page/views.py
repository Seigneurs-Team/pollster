import typing

from django.shortcuts import render

from databases.mysql_db import client_mysqldb
from Configs.Exceptions import NotFoundPoll, RepeatPollError, TryToXSS
from authentication.check_user_on_auth import authentication

import json

from django.http import JsonResponse, HttpResponseForbidden


@authentication()
def request_on_passing_poll_page(requests, poll_id: int, id_of_user: int = None):
    """
    Функция нужна для возврата страницы с прохождением конкретного опроса.
    Страница включает в себя все вопросы опроса, а также опции к этим опросам.

    :param requests:
    :param poll_id: идентификатор опроса
    :param id_of_user: идентификатор пользователя
    :return: render(requests, 'passing_poll_page.html', context={'user': user, 'poll': poll, 'is_pass': is_pass})
    или render(requests, 'NotFound.html')
    """
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
    try:
        client_mysqldb.add_users_into_table_for_users_who_pass_the_poll(id_of_user, id_of_poll)
        for answer in data_of_passing_poll['answers']:
            add_answers_into_db(answer, id_of_poll, id_of_user)
    except RepeatPollError:
        return HttpResponseForbidden()
    except TryToXSS:
        client_mysqldb.delete_cookie_from_session_table(auth_sessionid, 'auth_sessionid', id_of_user)
        return HttpResponseForbidden()
    else:
        return JsonResponse({'response': 200})


def add_answers_into_db(answer: dict, id_of_poll: int, id_of_user: int):
    """
    Функция исполняет сохранение данных, которые пользователь ввел в ответах на вопросы в опросе.
    :param answer: словарь с полями: question_id, type, value
    :param id_of_poll: идентификатор опроса
    :param id_of_user: идентификатор пользователя
    :return: None
    """
    serial_number = answer['question_id']
    type_of_question = answer['type']
    check_the_type(type_of_question)
    value: typing.Union[str, list] = answer['value']
    if isinstance(value, list):
        for value_of_list in value:
            client_mysqldb.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question, value_of_list, id_of_user, id_of_poll)
    elif isinstance(value, str):
        client_mysqldb.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question, value, id_of_user, id_of_poll)


def check_the_type(type_of_question: str):
    """
    Проверка значений поля type на несоответствие со значениями из БД.
    :param type_of_question: тип вопроса
    :return: None
    """
    types = client_mysqldb.get_types_of_question()
    if type_of_question not in types:
        raise TryToXSS("попытка XSS атаки")
