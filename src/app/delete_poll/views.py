from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from authentication.check_user_on_auth import authentication_for_delete_polls
from databases.mysql_db import client_mysqldb


@authentication_for_delete_polls
def request_on_delete_poll(request: WSGIRequest, id_of_poll: int):
    client_mysqldb.delete_poll(id_of_poll)
    return JsonResponse({'response': 200})