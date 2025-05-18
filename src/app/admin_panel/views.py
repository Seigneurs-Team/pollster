# тут все тупо скопировано с главной страницы, только admin_panel.html вместо index.html 


import dataclasses

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from databases.mysql_db import client_mysqldb

from authentication.check_user_on_auth import authentication_for_admin_panel


from Tools_for_rabbitmq.producer import producer
from Configs.Commands_For_RMQ import Commands
from Configs.Responses_from_consumer import Responses

from log_system.Levels import Levels

from Configs.Schemas.main_page import MAIN_PAGE_SCHEMA, GET_POLLS_SCHEMA


# @extend_schema(**MAIN_PAGE_SCHEMA)
# @api_view(['GET'])
@authentication_for_admin_panel
def request_on_admin_panel(requests: WSGIRequest, id_of_user: int = None):
    polls = client_mysqldb.get_polls(main_page=True)
    return render(requests, 'admin_panel.html', context={'all_objects': polls})


@extend_schema(**GET_POLLS_SCHEMA)
@api_view(['GET'])
def requests_on_get_polls(request, num_of_polls=5):
    """
    Функция нужна для получения выбранного количества опросов из БД
    :param request:
    :param num_of_polls: количество опросов

    :return: список опросов. Каждый элемент массива является экземпляром класса Poll
    """
    polls = [dataclasses.asdict(dataclass) for dataclass in client_mysqldb.get_polls(int(num_of_polls))]
    return JsonResponse({"list": polls})


def get_polls_for_user(id_of_user: int, polls: list):
    """
    Функция возвращает список опросов, которые рекомендательная система посчитала подходящими для конкретного пользователя.
    Отправляется запрос в контейнер consumer, который принимает значение ID_OF_POLL и NUM_OF_POLLS. После вычислений
    нейронной модели контейнер consumer возвращает список рекомендательных идентификаторов опросов.

    :param id_of_user: идентификатор пользователя

    :param polls: первичный список опросов, который может впоследствии изменить свое содержимое или нет

    :return: список опросов типа Poll
    """
    try:
        if client_mysqldb.check_existence_vector_of_user_from_ranking_table(id_of_user):
            response_of_rmq_request = producer.publish(Commands.get_similar_polls % (5, id_of_user))
            if response_of_rmq_request == Responses.RefusedConnection:
                raise AssertionError
            if response_of_rmq_request['response'] == Responses.UserPassAllPolls:
                polls = []
            elif response_of_rmq_request['response'] == Responses.Ok:
                list_polls_ids = response_of_rmq_request['polls_ids']
                polls = client_mysqldb.get_polls_by_their_id(list_polls_ids)
    except AssertionError:
        pass
    return polls

