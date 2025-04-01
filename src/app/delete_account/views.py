from authentication.check_user_on_auth import authentication
from databases.mysql_db import client_mysqldb

from django.http import JsonResponse


@authentication()
def request_on_delete_account(request, id_of_user: int = None):
    client_mysqldb.delete_entry_from_users(id_of_user)

    return JsonResponse({'response': 200})