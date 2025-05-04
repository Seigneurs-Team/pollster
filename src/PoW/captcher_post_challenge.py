from PoW.engine_of_PoW import EnginePoW

from django.http import JsonResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied

from databases.mysql_db import client_mysqldb

from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Configs.Schemas.create_new_account import GET_CHALLENGE_SCHEMA


@extend_schema(**GET_CHALLENGE_SCHEMA)
@api_view(['GET'])
def request_on_challenge(requests):
    """
    Функция нужна для хендла запроса на отправку данных для POW челленджа
    :param requests:
    :return: engine_of_pow.__dict__
    self.random_string = generate_random_string() if random_string is None else random_string
    self.timestamp = get_timestamp() if timestamp is None else timestamp
    self.count_of_bits = 3
    self.version = 1
    self.resource = 'pollster'
    self.extension = ''
    или
    403
    """
    try:
        assert 'auth_sessionid' in requests.COOKIES
        cookie = requests.COOKIES['auth_sessionid']
        engine_of_pow = EnginePoW()

        client_mysqldb.update_pow_in_pow_table(cookie, engine_of_pow.hash_cash_algorithm())

        return JsonResponse(engine_of_pow.__dict__)
    except AssertionError:
        raise PermissionDenied()