from authentication.check_user_on_auth import authentication

from django.core.handlers.wsgi import WSGIRequest
import json

from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Configs.Schemas.search_system import SEARCH_POLLS_SCHEMA


@extend_schema(**SEARCH_POLLS_SCHEMA)
@api_view(['GET'])
@authentication(False)
def request_on_get_search_polls(request: WSGIRequest, count_of_polls: int):
    json_data = json.loads(request.body)

