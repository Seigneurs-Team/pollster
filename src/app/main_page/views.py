from django.shortcuts import render
from django.http import JsonResponse
from databases.mysql_db import client_mysqldb

from authentication.check_user_on_auth import authentication_for_main_page


@authentication_for_main_page
def request_on_main_page(requests, is_authenticated: bool):
    polls = client_mysqldb.get_polls()
    tags = {  1: 'развлечения',  2: 'наука',  3: 'животные',  4: 'кухня',  5: 'искусство',  6: 'дети',  7: 'музыка',  8: 'кино и сериалы',  9: 'путешествия',  10: 'игры',  11: 'мода и стиль',  12: 'здоровье',  13: 'образование'}
    if is_authenticated is True:
        id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(requests.COOKIES['auth_sessionid'], 'auth_sessionid')
        nickname = client_mysqldb.get_user_nickname_from_table_with_cookie(requests.COOKIES['auth_sessionid'], 'auth_sessionid')

        user = {'is_authenticated': is_authenticated, 'id': id_of_user, 'username': nickname}
        return render(requests, 'index.html', context={'all_objects': polls, 'tags': tags.items(), 'user': user})
    else:
        user = {'is_authenticated': is_authenticated}
        return render(requests, 'index.html', context={'all_objects': polls, 'tags': tags.items(), 'user': user})


def requests_on_get_polls(request, num_of_polls=5):
    polls = client_mysqldb.get_polls(int(num_of_polls))
    return JsonResponse({"list": polls})


