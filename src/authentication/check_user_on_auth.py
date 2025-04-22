import mysql.connector.errors

from databases.mysql_db import client_mysqldb
from Configs.Exceptions import CookieWasExpired, NotFoundPoll

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound


def check_user(request, get_id_of_user: bool = False):
    """
    Функция нужна для проверки на то, что клиент с куки auth_sessionid авторизован в системе
    :param request:
    :param get_id_of_user: возвращать id_of_user или никнейм
    :return: id_of_user или никнейм
    """
    assert 'auth_sessionid' in request.COOKIES
    auth_sessionid = request.COOKIES['auth_sessionid']
    if get_id_of_user is False:
        user = client_mysqldb.get_user_nickname_from_table_with_cookie(auth_sessionid, 'auth_sessionid')
        assert user is not None
        return user
    else:
        id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(auth_sessionid, 'auth_sessionid')
        assert id_of_user is not None
        return id_of_user


def authentication(return_id_of_user: bool = True):
    """
    Декоратор является точкой проверки подлинности авторизации клиента в системе

    :param return_id_of_user: параметр определяет возвращать id_of_user в kwargs или нет

    :return: return func(request, *args, **kwargs)
    """
    def wrapped_func_main(func):
        def wrapped_func(request: WSGIRequest, *args, **kwargs):
            try:
                id_of_user = check_user(request, get_id_of_user=True)
                if return_id_of_user:
                    kwargs['id_of_user'] = id_of_user
                return func(request, *args, **kwargs)
            except (AssertionError, CookieWasExpired) as _ex:
                return HttpResponseRedirect('/sign_in')
        return wrapped_func
    return wrapped_func_main


def authentication_for_profile_page(func):
    """
    Функция нужна для проверки на подлинность пользователя на странице пользователя

    :param func:
    :return:
    """
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
    """
    Функция нужна для проверки на то, что пользователь авторизован в системе.
    Это нужно для главной страницы, чтобы определить рекомендовать ли пользователю опросы или нет.

    :param func:
    :return:
    """
    def wrapped_func(request: WSGIRequest, *args, **kwargs):
        try:
            check_user(request)
            return func(request, True)
        except AssertionError:
            return func(request, False)
    return wrapped_func


def authentication_for_delete_polls(func):
    """
    Декоратор нужен для того, чтобы удалить опрос на странице профиля. Проверяется id_of_user и id_of_author
    и если значение одинаковы, то появляется возможность удалить опрос. Иначе вернет 403

    :param func:
    :return:
    """
    def wrapped_func(request: WSGIRequest, id_of_poll: int, *args, **kwargs):
        try:
            check_user(request)

            id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(request.COOKIES['auth_sessionid'], 'auth_sessionid')
            id_of_author = client_mysqldb.get_id_of_author_of_poll(id_of_poll)

            assert (id_of_user == id_of_author) or client_mysqldb.check_user_into_superusers(id_of_user)

            return func(request, id_of_poll, *args, **kwargs)

        except AssertionError:
            return HttpResponseForbidden()
        except NotFoundPoll:
            return HttpResponseNotFound()
    return wrapped_func


def authentication_for_change_user_data(func):
    """
    Функция нужна для изменения данных пользователя. Функция проверяет на подлинность клиента после чего изменяет данные
    :param func:
    :return:
    """
    def wrapped_func(request: WSGIRequest, *args, **kwargs):
        try:
            id_of_user = check_user(request, get_id_of_user=True)
            kwargs['id_of_user'] = id_of_user
            return func(request, *args, **kwargs)
        except mysql.connector.errors.DataError:
            return HttpResponseForbidden('некорректная длинна поля')
        except (AssertionError, CookieWasExpired) as _ex:
            return HttpResponseRedirect('/sign_in')
    return wrapped_func


def authentication_for_passing_poll_page(func):
    def wrapped_func(request: WSGIRequest, *args, **kwargs):
        try:
            id_of_user = check_user(request, get_id_of_user=True)
            kwargs['id_of_user'] = id_of_user
            if type(kwargs['poll_id']) is int:
                if client_mysqldb.check_poll_on_private(kwargs["poll_id"]):
                    return HttpResponseForbidden()
            return func(request, *args, **kwargs)
        except (AssertionError, CookieWasExpired) as _ex:
            return HttpResponseRedirect('/sign_in')

    return wrapped_func


def authentication_for_statistics(return_id_of_user: bool = True):
    def wrapped_high_func(func):
        def wrapped_func(request: WSGIRequest, *args, **kwargs):
            try:
                id_of_user = check_user(request, get_id_of_user=True)
                if return_id_of_user:
                    kwargs['id_of_user'] = id_of_user
                if client_mysqldb.check_poll_on_private(kwargs['id_of_poll']):
                    if id_of_user == client_mysqldb.get_metadata_of_poll(kwargs['id_of_poll'])[3]:
                        return func(request, *args, **kwargs)
                    else:
                        return HttpResponseForbidden()
            except (AssertionError, CookieWasExpired) as _ex:
                return HttpResponseRedirect('/sign_in')
        return wrapped_func
    return wrapped_high_func