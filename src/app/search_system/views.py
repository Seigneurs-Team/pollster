from authentication.check_user_on_auth import authentication

from django.core.handlers.wsgi import WSGIRequest
from django.http.response import JsonResponse
import json

from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Configs.Schemas.search_system import SEARCH_POLLS_SCHEMA

from databases.mysql_db import client_mysqldb


@extend_schema(**SEARCH_POLLS_SCHEMA)
@api_view(['POST'])
@authentication(False)
def request_on_get_search_polls(request: WSGIRequest):
    try:
        json_data = json.loads(request.body)

        count_of_polls = json_data['count_of_poll']
        tags = json_data['tags']
        name_of_poll_for_search = json_data['name_of_poll_for_search']

        list_of_polls = None

        return JsonResponse({'list_of_polls': list_of_polls})
    except IndexError:
        return JsonResponse({'response': 'Неправильные поля в теле запроса.'}, status=400)
