from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest
from databases.mysql_db import client_mysqldb
from Configs.Poll import Poll
from random import randint


def request_on_main_page(requests):
    polls = client_mysqldb.get_polls()
    return render(requests, 'index.html', context={'all_objects': polls})


def requests_on_get_polls(request, num_of_polls):
    return JsonResponse({"list": client_mysqldb.get_polls(int(num_of_polls))})


def request_on_create_new_poll(request: HttpRequest):
    print(list(request.FILES.items()))
    poll: Poll = Poll(request.POST.get("description", ''), request.POST.get("name_of_poll", ''), request.POST.get("tags", ""), randint(1, 100000))
    result = client_mysqldb.create_poll(poll)
    return JsonResponse({"result": result})
