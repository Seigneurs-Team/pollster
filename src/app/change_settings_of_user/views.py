import json
from django.core.handlers.wsgi import WSGIRequest

from authentication.check_user_on_auth import authentication
from databases.mysql_db import client_mysqldb


@authentication
def request_on_change_the_nickname(request: WSGIRequest, id_of_user: int):
    json_data = json.loads(request.body)
    assert 'nickname' in json_data

    client_mysqldb.update_the_filed_into_users(id_of_user, 'nickname', json_data['nickname'])



