import json

import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest
from databases.mysql_db import client_mysqldb
from Configs.Poll import Poll
from random import randint


def request_on_create_poll_page(requests):
    polls = client_mysqldb.get_polls()
    return render(requests, 'create_poll_page.html', context={'all_objects': polls})


def requests_on_get_polls(request, num_of_polls=5):
    polls = client_mysqldb.get_polls(int(num_of_polls))
    return JsonResponse({"list": polls})


def request_on_create_new_poll(request: HttpRequest):
    json_data = json.loads(request.body)
    poll: Poll = Poll(json_data.get("description", ''), json_data.get("name_of_poll", ''), json_data.get("tags", ""), randint(1, 100000))
    result = client_mysqldb.create_poll(poll)
    return JsonResponse({"result": result})
