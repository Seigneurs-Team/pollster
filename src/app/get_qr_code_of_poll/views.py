from django.http.response import JsonResponse
from databases.mysql_db import client_mysqldb
from src.generate_qr_code import generate_qr_code_of_link
from Configs.Hosts import Hosts


def request_of_get_qr_code(id_of_poll: int):
    qr_code_of_poll = {}
    if client_mysqldb.check_poll_on_private(id_of_poll):
        code = client_mysqldb.get_code_from_private_polls(id_of_poll)
        qr_code_of_poll['qr_code'] = generate_qr_code_of_link("http://%s/%s" % (Hosts.domain, code))
        qr_code_of_poll['url_on_poll'] = "http://%s/%s" % (Hosts.domain, code)

        return JsonResponse({qr_code_of_poll})
    else:
        qr_code_of_poll['qr_code'] = generate_qr_code_of_link("http://%s/%s" % (Hosts.domain, id_of_poll))
        qr_code_of_poll['url_on_poll'] = "http://%s/%s" % (Hosts.domain, id_of_poll)

        return JsonResponse(qr_code_of_poll)
