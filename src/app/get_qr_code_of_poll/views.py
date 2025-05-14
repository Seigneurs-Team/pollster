from django.http.response import JsonResponse
from databases.mysql_db import client_mysqldb
from generate_qr_code import generate_qr_code_of_link
from Configs.Hosts import Hosts

from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import PermissionDenied

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

from authentication.check_user_on_auth import authentication


from Configs.Schemas.get_qr_code import GET_QR_CODE_SCHEMA


@extend_schema(**GET_QR_CODE_SCHEMA)
@api_view(['GET'])
@authentication(False)
def request_on_get_qr_code(request: WSGIRequest, id_of_poll: int):
    qr_code_of_poll = {}
    if client_mysqldb.check_poll_on_private(id_of_poll):
        if client_mysqldb.get_id_of_author_of_poll(id_of_poll) != client_mysqldb.get_id_of_user_from_table_with_cookies(
                request.COOKIES['auth_sessionid'], 'auth_sessionid'
        ):
            raise PermissionDenied()
        code = client_mysqldb.get_code_from_private_polls(id_of_poll)
        qr_code_of_poll['qr_code'] = generate_qr_code_of_link("http://%s/%s" % (Hosts.domain, code))
        qr_code_of_poll['url_on_poll'] = "http://%s/%s" % (Hosts.domain, code)

        return JsonResponse(qr_code_of_poll)
    else:
        qr_code_of_poll['qr_code'] = generate_qr_code_of_link("http://%s/%s" % (Hosts.domain, id_of_poll))
        qr_code_of_poll['url_on_poll'] = "http://%s/%s" % (Hosts.domain, id_of_poll)

        return JsonResponse(qr_code_of_poll)
