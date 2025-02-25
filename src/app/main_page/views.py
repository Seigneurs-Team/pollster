import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest
from databases.mysql_db import client_mysqldb
from Configs.Poll import Poll
from random import randint


def request_on_main_page(requests):
    polls = client_mysqldb.get_polls()
    return render(requests, 'index.html', context={'all_objects': polls, 'tags': ['first tag', 'second tag', 'third tag', 'fourth tag', 'fifth tag', 'sixth tag', 'seventh tag']})


def requests_on_get_polls(request, num_of_polls=5):
    polls = client_mysqldb.get_polls(int(num_of_polls))
    return JsonResponse({"list": polls})


