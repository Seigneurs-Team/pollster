import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseForbidden
from databases.mysql_db import client_mysqldb
from app.create_poll_page.set_poll import set_poll
from Configs.Exceptions import TryToXSS


def request_on_create_poll_page(requests):
    # тут должна быть проверка, выполнен ли вход в аккаунт. если да, то user извлекается из БД (id, username и фото профиля в дальнейшем)
    user = {'id' : 123, 'username' : "DikayaKakEnot"}
    return render(requests, 'create_poll_page.html', context={'user': user})


def requests_on_get_polls(request, num_of_polls=5):
    polls = client_mysqldb.get_polls(int(num_of_polls))
    return JsonResponse({"list": polls})


def request_on_create_new_poll(request: HttpRequest):
    json_data = json.loads(request.body)
    try:
        poll, list_of_questions, list_of_options, list_of_right_answers, list_right_text_answer = set_poll(json_data)
        result = client_mysqldb.create_pool(
            poll, list_of_questions, list_of_options, list_of_right_answers, list_right_text_answer
        )
        return JsonResponse({"result": result})
    except TryToXSS:
        return HttpResponseForbidden()
