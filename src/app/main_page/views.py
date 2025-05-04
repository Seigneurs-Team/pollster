import dataclasses
from Configs.Serializers import ListOfPolls

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework.decorators import api_view

from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from databases.mysql_db import client_mysqldb

from authentication.check_user_on_auth import authentication_for_main_page


from Tools_for_rabbitmq.producer import producer
from Configs.Commands_For_RMQ import Commands
from Configs.Responses_from_consumer import Responses
from Configs.Poll import Poll

from log_system.Levels import Levels


@extend_schema(
    summary='получение главной страницы',
    tags=['main page'],
    description='Endpoint нужен для получения HTML главной страницы, а также получения рекомендательных опросов, если пользователь авторизован в системе.',
    methods=['GET'],
    responses={
        200: OpenApiResponse(description='Запрос успешно был обработан. Выдан HTML главной страницы.')
    }
)
@api_view(['GET'])
@authentication_for_main_page
def request_on_main_page(requests: WSGIRequest, is_authenticated: bool):
    """
    Функция нужна для отправки клиенту страницы html. Если пользователь авторизован в системе, то ему будут подобраны опросы
    с помощью рекомендательной системы, иначе будут выданы первые пять опросов из БД.

    :param requests:
    :param is_authenticated: если True, то авторизованный пользователь отправляет запрос на загрузку страницы,
    если False, то неавторизованный пользователь отправляет запрос на сервер.
    Переменная нужна для понимания, какие опросы отправлять обратно клиенту.

    :return: render(requests, 'index.html', context={'all_objects': polls, 'tags': tags, 'user': user})
    """
    polls = client_mysqldb.get_polls(main_page=True)
    tags = ['развлечения', 'наука', 'животные', 'кухня', 'искусство', 'дети', 'музыка', 'кино и сериалы', 'путешествия', 'игры', 'мода и стиль', 'здоровье', 'образование']
    if is_authenticated is True:
        id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(requests.COOKIES['auth_sessionid'], 'auth_sessionid')
        producer.publish_log('Получил запрос на рендеринг главной страницы', Levels.Debug, id_of_user, requests=requests)

        nickname = client_mysqldb.get_user_nickname_from_table_with_cookie(requests.COOKIES['auth_sessionid'], 'auth_sessionid')
        user = {'is_authenticated': is_authenticated, 'id': id_of_user, 'username': nickname}
        polls = client_mysqldb.get_polls(only_for_user=True, id_of_user=id_of_user)

        polls = get_polls_for_user(id_of_user, polls)

    else:
        producer.publish_log('Получил запрос на рендеринг главной страницы', Levels.Debug, None, requests=requests)

        user = {'is_authenticated': is_authenticated}
    return render(requests, 'index.html', context={'all_objects': polls, 'tags': tags, 'user': user})


@extend_schema(
    summary='Получение списка опросов из БД.',
    description='Endpoint нужен для выборки n-го количества опросов из БД MySQL.',
    parameters=[
        OpenApiParameter(
            name='num_of_polls',
            location=OpenApiParameter.PATH,
            description='Параметр обозначает количество опросов, которые необходимо вернуть.',
            required=False,
            type=int
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Список опросов.',
            response=ListOfPolls
        )
    }
)
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

