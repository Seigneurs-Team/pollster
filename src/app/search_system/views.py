from authentication.check_user_on_auth import authentication

from django.core.handlers.wsgi import WSGIRequest
import json

from rest_framework.decorators import api_view


@api_view(['POST'])
@authentication(False)
def request_on_get_search_polls(request: WSGIRequest):
    json_data = json.loads(request.body)

