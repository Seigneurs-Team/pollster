# тут все тупо скопировано с главной страницы, только admin_panel.html вместо index.html 


import dataclasses

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from databases.mysql_db import client_mysqldb

from authentication.check_user_on_auth import authentication_for_admin_panel


from Configs.Schemas.admin_panel import GET_ADMIN_PANEL_SCHEMA, BAN_USER_SCHEMA, UNBAN_SCHEMA


@extend_schema(**GET_ADMIN_PANEL_SCHEMA)
@api_view(['GET'])
@authentication_for_admin_panel
def request_on_admin_panel(requests: WSGIRequest):
    polls = client_mysqldb.get_polls(main_page=True)
    return render(requests, 'admin_panel.html', context={'all_objects': polls})


@extend_schema(**BAN_USER_SCHEMA)
@api_view(['POST'])
@authentication_for_admin_panel
def request_on_ban_user(request: WSGIRequest, id_of_user: int):
    try:
        client_mysqldb.create_entry_into_ban_users(id_of_user)
    except AssertionError:
        return JsonResponse({'response': 'Пользователь не найден.'}, status=404)

    return JsonResponse({'responses': 'Пользователь успешно заблокирован в системе.'})


@extend_schema(**UNBAN_SCHEMA)
@api_view(['POST'])
@authentication_for_admin_panel
def request_on_unban_user(requst: WSGIRequest, id_of_user: int):
    try:
        client_mysqldb.delete_entry_from_ban_users(id_of_user)
        return JsonResponse({'response': 'Пользователь успешно разблокирован в системе.'})
    except AssertionError:
        return JsonResponse({'response': 'Пользователь не найден.'}, status=404)
