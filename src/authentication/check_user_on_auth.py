from databases.mysql_db import client_mysqldb
from Configs.Exceptions import CookieWasExpired

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect, HttpResponseForbidden


def check_user(request):
    assert 'auth_sessionid' in request.COOKIES
    auth_sessionid = request.COOKIES['auth_sessionid']
    user = client_mysqldb.get_user_nickname_from_table_with_cookie(auth_sessionid, 'auth_sessionid')
    assert user is not None
    return user


def authentication(func):
    def wrapped_func(request: WSGIRequest, *args, **kwargs):
        try:
            check_user(request)
            return func(request, *args, **kwargs)
        except (AssertionError, CookieWasExpired) as _ex:
            return HttpResponseRedirect('/sign_in')
    return wrapped_func


def authentication_for_profile_page(func):
    def wrapped_func(request: WSGIRequest, id_of_user: int, *args, **kwargs):
        try:
            user_nickname = check_user(request)
            nickname = client_mysqldb.get_user_data_from_table(id_of_user)[0]

            assert user_nickname == nickname

            return func(request, id_of_user, *args, **kwargs)
        except AssertionError:
            return HttpResponseForbidden()
    return wrapped_func


def authentication_for_main_page(func):
    def wrapped_func(request: WSGIRequest, *args, **kwargs):
        try:
            check_user(request)
            return func(request, True)
        except AssertionError:
            return func(request, False)
    return wrapped_func