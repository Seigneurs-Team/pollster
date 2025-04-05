from django.core.handlers.wsgi import WSGIRequest
from django.http.response import JsonResponse
from django.shortcuts import render

from databases.mysql_db import client_mysqldb
from authentication.check_user_on_auth import authentication


@authentication()
def request_on_statistics_page(requests: WSGIRequest, id_of_poll: int, id_of_user: int = None):
    nickname = client_mysqldb.get_user_nickname_from_table_with_cookie(requests.COOKIES['auth_sessionid'], 'auth_sessionid')
    user = {'id': id_of_user, 'username': nickname}

    return render(requests, 'statistics_page.html', context={'id_of_poll': id_of_poll, 'user': user})


@authentication(False)
def request_on_get_statistics(requests: WSGIRequest, id_of_poll: int):
    count_of_users_who_pass_the_poll = client_mysqldb.get_count_of_users_who_pass_the_poll(id_of_poll)
    list_of_questions = [question[4:] for question in client_mysqldb.get_questions(id_of_poll)]
    dict_for_statistics: dict = {
        'count_of_users': count_of_users_who_pass_the_poll,
        'questions': []
    }

    for question in list_of_questions:
        dict_of_questions: dict = {
            'id': question[0],
            'type_of_question': question[1],
            'text_of_question': question[2],
            'serial_number': question[3]
        }

        if dict_of_questions['type_of_question'] == 'radiobutton' or \
                dict_of_questions['type_of_question'] == 'checkbox':
            list_of_options_name = client_mysqldb.get_options(dict_of_questions['id'])
            list_of_right_answer_ids = client_mysqldb.get_right_answers(dict_of_questions['id'])

            dict_of_questions['options'] = set_options(
                list_of_options_name, list_of_right_answer_ids,
                dict_of_questions['seral_number'], id_of_poll
            )
        else:
            dict_of_questions['text_answers'] = client_mysqldb.get_text_answers_of_users(id_of_poll, dict_of_questions['serial_number'])
            dict_of_questions['right_text_answer'] = client_mysqldb.get_text_right_answers(dict_of_questions['id'])

        dict_for_statistics['questions'].append(dict_of_questions)

    return JsonResponse(dict_for_statistics)


def set_options(list_of_options_name: list, list_of_right_answer_ids: list, serial_number: int, id_of_poll: int):
    list_of_options: list[dict] = []
    for index, option in enumerate(list_of_options_name):
        list_of_options.append({
            option: {
                "count_of_selected": client_mysqldb.get_count_of_users_who_selected_of_specific_option(option, serial_number, id_of_poll),
                'is_right_answer': index in list_of_right_answer_ids
            }
        })
    return list_of_options







