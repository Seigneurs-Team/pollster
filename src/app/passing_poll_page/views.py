import typing

from django.shortcuts import render

from databases.mysql_db import client_mysqldb
from Configs.Exceptions import NotFoundPoll, RepeatPollError
from authentication.check_user_on_auth import authentication

import json

from django.http import JsonResponse, HttpResponseForbidden


@authentication
def request_on_passing_poll_page(requests, poll_id):
    # получение опроса по id
    auth_sessionid = requests.COOKIES['auth_sessionid']
    id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(auth_sessionid, 'auth_sessionid')
    nickname = client_mysqldb.get_user_nickname_from_table_with_cookie(auth_sessionid, 'auth_sessionid')

    user = {'id': id_of_user, 'username': nickname}
    try:
        poll = client_mysqldb.get_poll(poll_id)
        return render(requests, 'passing_poll_page.html', context={'user': user, 'poll': poll})
    except NotFoundPoll as _ex:
        return render(requests, 'NotFound.html')


@authentication
def request_on_passing_poll(request):
    try:
        data_of_passing_poll = json.loads(request.body)
        auth_sessionid = request.COOKIES['auth_sessionid']
        id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(auth_sessionid, 'auth_sessionid')

        id_of_poll = data_of_passing_poll['poll_id']

        client_mysqldb.add_users_into_table_for_users_who_pass_the_poll(id_of_user, id_of_poll)
        for answer in data_of_passing_poll['answers']:
            add_answers_into_db(answer, id_of_poll, id_of_user)
    except RepeatPollError:
        return HttpResponseForbidden()
    else:
        return JsonResponse({'response': 200})


def add_answers_into_db(answer: dict, id_of_poll: int, id_of_user: int):
    serial_number = answer['question_id']
    type_of_question = answer['type']
    value: typing.Union[str, list] = answer['value']
    if isinstance(value, list):
        for value_of_list in value:
            client_mysqldb.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question, value_of_list, id_of_user, id_of_poll)
    elif isinstance(value, str):
        client_mysqldb.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question, value, id_of_user, id_of_poll)
