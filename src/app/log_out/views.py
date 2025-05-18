from authentication.check_user_on_auth import authentication
from databases.mysql_db import client_mysqldb
from django.http.response import JsonResponse

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

from Configs.Schemas.log_out import LOG_OUT_SCHEMA


@extend_schema(**LOG_OUT_SCHEMA)
@api_view(['POST'])
@authentication()
def request_on_log_out(request, id_of_user: int = None):
    """
    Функция позволяет завершить сессию пользователя. В БД удаляется соответствующая запись с ключом id_of_user
    :param request:
    :param id_of_user: идентификатор пользователя
    :return: 200
    """
    client_mysqldb.delete_cookie_from_session_table(request.COOKIES['auth_sessionid'], 'auth_sessionid', id_of_user)
    return JsonResponse({'response': 'Пользователь успешно вышел из аккаунта.'})

