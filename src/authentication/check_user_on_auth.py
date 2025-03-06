from databases.mysql_db import client_mysqldb
from Configs.Exceptions import CookieWasExpired

from typing import Optional

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect


def authentication(func):
    def wrapped_func(request: WSGIRequest, *args, **kwargs):
        try:
            assert 'auth_sessionid' in request.COOKIES
            auth_sessionid = request.COOKIES['auth_sessionid']
            user = client_mysqldb.get_user_nickname_from_table_with_cookie(auth_sessionid, 'auth_sessionid')
            assert user is not None
            return func(request, *args, **kwargs)
        except (AssertionError, CookieWasExpired) as _ex:
            return HttpResponseRedirect('/sign_in')
    return wrapped_func




