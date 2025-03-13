import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseForbidden
from databases.mysql_db import client_mysqldb
from app.create_poll_page.set_poll import set_poll
from Configs.Exceptions import TryToXSS

from authentication.check_user_on_auth import authentication


@authentication
def request_on_create_poll_page(requests):
    id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(requests.COOKIES['auth_sessionid'], 'auth_sessionid')
    nickname = client_mysqldb.get_user_nickname_from_table_with_cookie(requests.COOKIES['auth_sessionid'], 'auth_sessionid')

    user = {'id': id_of_user, 'username': nickname}
    return render(requests, 'create_poll_page.html', context={'user': user})


def requests_on_get_polls(request, num_of_polls=5):
    polls = client_mysqldb.get_polls(int(num_of_polls))
    return JsonResponse({"list": polls})


@authentication
def request_on_create_new_poll(request: HttpRequest):
    id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(request.COOKIES['auth_sessionid'], 'auth_sessionid')
    json_data = json.loads(request.body)
    try:
        poll, list_of_questions, list_of_options, list_of_right_answers, list_right_text_answer = set_poll(json_data, id_of_user)
        result = client_mysqldb.create_pool(
            poll, list_of_questions, list_of_options, list_of_right_answers, list_right_text_answer
        )
        return JsonResponse({"result": result})
    except TryToXSS:
        return HttpResponseForbidden()
