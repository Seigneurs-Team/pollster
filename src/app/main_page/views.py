from django.shortcuts import render
from django.http import JsonResponse
from databases.mysql_db import client_mysqldb

from authentication.check_user_on_auth import authentication_for_main_page


from Tools_for_rabbitmq.producer import producer
from Configs.Commands_For_RMQ import Commands
from Configs.Responses_from_consumer import Responses


@authentication_for_main_page
def request_on_main_page(requests, is_authenticated: bool):
    polls = client_mysqldb.get_polls()
    tags = ['развлечения', 'наука', 'животные', 'кухня', 'искусство', 'дети', 'музыка', 'кино и сериалы', 'путешествия', 'игры', 'мода и стиль', 'здоровье', 'образование']
    if is_authenticated is True:
        id_of_user = client_mysqldb.get_id_of_user_from_table_with_cookies(requests.COOKIES['auth_sessionid'], 'auth_sessionid')
        nickname = client_mysqldb.get_user_nickname_from_table_with_cookie(requests.COOKIES['auth_sessionid'], 'auth_sessionid')
        user = {'is_authenticated': is_authenticated, 'id': id_of_user, 'username': nickname}

        polls = get_polls_for_user(id_of_user, polls)

    else:
        user = {'is_authenticated': is_authenticated}
    return render(requests, 'index.html', context={'all_objects': polls, 'tags': tags, 'user': user})


def requests_on_get_polls(request, num_of_polls=5):
    polls = client_mysqldb.get_polls(int(num_of_polls))
    return JsonResponse({"list": polls})


def get_polls_for_user(id_of_user: int, polls: list):
    try:
        if client_mysqldb.get_vector_of_user_from_ranking_table(id_of_user):
            response_of_rmq_request = producer.publish(Commands.get_similar_polls % (5, id_of_user))
            if response_of_rmq_request is None:
                raise AssertionError
            if response_of_rmq_request['response'] == Responses.UserPassAllPolls:
                polls = []
            elif response_of_rmq_request['response'] == Responses.Ok:
                list_polls_ids = response_of_rmq_request['polls_ids']
                polls = client_mysqldb.get_polls_by_their_id(list_polls_ids)
    except AssertionError:
        pass
    return polls

