from authentication.check_user_on_auth import authentication
from databases.mysql_db import client_mysqldb

from django.http import JsonResponse


from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

from Configs.Schemas.delete_account import DELETE_ACCOUNT_SCHEMA


@extend_schema(**DELETE_ACCOUNT_SCHEMA)
@api_view(['DELETE'])
@authentication()
def request_on_delete_account(request, id_of_user: int = None):
    """
    Функция нужна для удаления пользователя из БД, а также всех связанных с ним записей во всех таблицах по id_of_user

    :param request:
    :param id_of_user: идентификатор пользователя
    :return: 200
    """
    client_mysqldb.delete_entry_from_users(id_of_user)

    return JsonResponse({'response': 'Учетная запись успешно удалена.'})