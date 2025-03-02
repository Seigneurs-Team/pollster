import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest
from databases.mysql_db import client_mysqldb
from Configs.Poll import Poll
from random import randint


def request_on_main_page(requests):
    polls = client_mysqldb.get_polls()
    # tags - это для фильтров
    tags = ['first tag', 'second tag', 'third tag', 'fourth tag', 'fifth tag', 'sixth tag', 'seventh tag']
    # этот user временный. в реале через куки проверяется, выполнен ли вход в аккаунт, и из БД извлекается user.
    user = {'is_authenticated' : True, 'id' : 123, 'username' : "DikayaKakEnot"} # поменять 'is_authenticated' на False, чтобы увидеть кнопку "войти"
    return render(requests, 'index.html', context={'all_objects': polls, 'tags': tags, 'user': user})



def requests_on_get_polls(request, num_of_polls=5):
    polls = client_mysqldb.get_polls(int(num_of_polls))
    return JsonResponse({"list": polls})


