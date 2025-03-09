from authentication.check_user_on_auth import authentication
from databases.mysql_db import client_mysqldb

from django.http import JsonResponse


@authentication
def request_on_delete_account(request):
    id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(request.COOKIES['auth_sessionid'], 'auth_sessionid')
    client_mysqldb.delete_entry_from_users(id_of_user)

    return JsonResponse({'response': 200})