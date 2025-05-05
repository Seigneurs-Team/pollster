from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from authentication.check_user_on_auth import authentication_for_delete_polls
from databases.mysql_db import client_mysqldb

from Configs.Schemas.delete_poll import DELETE_POLL_SCHEMA

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view


@extend_schema(**DELETE_POLL_SCHEMA)
@api_view(['DELETE'])
@authentication_for_delete_polls
def request_on_delete_poll(request: WSGIRequest, id_of_poll: int):
    """
    Функция нужна для удаления опроса в БД, а также всех записей связанных с ним по id_of_poll
    :param request:
    :param id_of_poll: идентификатор опроса
    :return: 200
    """
    client_mysqldb.delete_poll(id_of_poll)
    return JsonResponse({'response': 'Опрос был успешно удален.'})