import json
from generate_qr_code import generate_qr_code_of_link

from django.core.handlers.wsgi import WSGIRequest
from django.http.response import JsonResponse
from django.shortcuts import render

from databases.mysql_db import client_mysqldb
from authentication.check_user_on_auth import authentication_for_statistics

from Configs.Hosts import Hosts


@authentication_for_statistics()
def request_on_statistics_page(requests: WSGIRequest, id_of_poll: int, id_of_user: int = None):
    """
    Функция нужна для возврата страницы со статистикой опроса
    :param requests:
    :param id_of_poll: идентификатор опроса
    :param id_of_user: идентификатор пользователя
    :return: render(requests, 'statistics_page.html', context={'id_of_poll': id_of_poll, 'user': user})
    """
    nickname = client_mysqldb.get_user_nickname_from_table_with_cookie(requests.COOKIES['auth_sessionid'], 'auth_sessionid')
    user = {'id': id_of_user, 'username': nickname}

    dict_of_statistic = get_statistic(id_of_poll)

    context: dict = {'id_of_poll': id_of_poll, 'user': user, 'questions': dict_of_statistic}

    if client_mysqldb.check_poll_on_private(id_of_poll):
        code = client_mysqldb.get_code_from_private_polls(id_of_poll)
        context['qr_code'] = generate_qr_code_of_link("http://%s/%s" % (Hosts.domain, code))
        context['url_on_poll'] = "http://%s/%s" % (Hosts.domain, code)

    return render(requests, 'statistics_page.html', context=context)


@authentication_for_statistics(False)
def request_on_get_statistics(requests: WSGIRequest, id_of_poll: int):
    """
    Функция нужна для получения статистики по конкретному опросу.
    :param requests:
    :param id_of_poll: идентификатор опроса

    :return: словарь состоящий из списка словарей вопросов, количества пройденных пользователей
    """
    dict_for_statistics = get_statistic(id_of_poll, True)

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


def get_the_count_of_right_and_wrong_answers(list_of_options_name: list, list_of_right_answer_ids: list, serial_number: int, id_of_poll: int) -> (int, int):
    count_of_right_answers: int = 0
    count_of_wrong_answers: int = 0

    for index, option in enumerate(list_of_options_name):
        if index in list_of_right_answer_ids:
            count_of_right_answers += client_mysqldb.get_count_of_users_who_selected_of_specific_option(option, serial_number, id_of_poll)
        else: count_of_wrong_answers += client_mysqldb.get_count_of_users_who_selected_of_specific_option(option, serial_number, id_of_poll)

    return count_of_right_answers, count_of_wrong_answers


def get_statistic(id_of_poll: int, more_statistic: bool = False) -> dict:
    count_of_users_who_pass_the_poll = client_mysqldb.get_count_of_users_who_pass_the_poll(id_of_poll)
    list_of_questions = [question[4:] for question in client_mysqldb.get_questions(id_of_poll)]
    metadata_of_poll = client_mysqldb.get_metadata_of_poll(id_of_poll)
    dict_for_statistics: dict = {
        'count_of_users': count_of_users_who_pass_the_poll,
        'name_of_poll': metadata_of_poll[0],
        'description_of_poll': metadata_of_poll[1],
        'tags_of_poll': json.loads(metadata_of_poll[2]),
        'author': metadata_of_poll[3],
        'questions': [],
    }

    for question in list_of_questions:
        dict_of_questions: dict = {
            'id': question[0],
            'type_of_question': question[1],
            'text_of_question': question[2],
            'serial_number': question[3]
        }

        if dict_of_questions['type_of_question'] == 'radio' or \
                dict_of_questions['type_of_question'] == 'checkbox':
            dict_of_questions = set_statistic_for_radiobutton_of_checkbox_questions(dict_of_questions, id_of_poll, more_statistic)
        elif dict_of_questions['type_of_question'] == 'long text':
            dict_of_questions = set_statistic_for_long_text_questions(dict_of_questions, id_of_poll, more_statistic)
        elif dict_of_questions['type_of_question'] == 'short text':
            dict_of_questions = set_statistic_for_short_text_questions(dict_of_questions, id_of_poll, more_statistic)

        dict_for_statistics['questions'].append(dict_of_questions)

    return dict_for_statistics


def set_statistic_for_radiobutton_of_checkbox_questions(dict_of_questions: dict, id_of_poll: int, more_statistic: bool):
    list_of_options_name = client_mysqldb.get_options(dict_of_questions['id'])
    list_of_right_answer_ids = client_mysqldb.get_right_answers(dict_of_questions['id'])

    if more_statistic:
        count_of_right_answers, count_of_wrong_answers = get_the_count_of_right_and_wrong_answers(
            list_of_options_name, list_of_right_answer_ids, dict_of_questions['serial_number'], id_of_poll
        )
        dict_of_questions['num_of_right_answers'] = count_of_right_answers
        dict_of_questions['num_of_wrong_answers'] = count_of_wrong_answers

    dict_of_questions['options'] = set_options(
        list_of_options_name, list_of_right_answer_ids,
        dict_of_questions['serial_number'], id_of_poll
    )

    return dict_of_questions


def set_statistic_for_long_text_questions(dict_of_questions: dict, id_of_poll: int, more_statistic: bool):
    if more_statistic:
        dict_of_questions['count_of_writes'] = client_mysqldb.get_count_of_text_answers(
            dict_of_questions['id'], dict_of_questions['serial_number'], dict_of_questions['type_of_question']
        )
    else:
        dict_of_questions['text_answers'] = [{'text': answer} for answer in client_mysqldb.get_text_answers_of_users(
            id_of_poll, dict_of_questions['serial_number']
        )]

    return dict_of_questions


def set_statistic_for_short_text_questions(dict_of_questions: dict, id_of_poll, more_statistic: bool):
    if more_statistic:
        dict_of_questions['count_of_writes'] = client_mysqldb.get_count_of_text_answers(
            dict_of_questions['id'],
            dict_of_questions['serial_number'],
            dict_of_questions['type_of_question']
        )
        dict_of_questions['num_of_right_answers'] = client_mysqldb.get_count_of_right_answers(
            id_of_poll,
            dict_of_questions['serial_number']
        )
        dict_of_questions['num_of_wrong_answers'] = client_mysqldb.get_count_of_wrong_answers(
            id_of_poll,
            dict_of_questions['serial_number']
        )
    else:
        dict_of_questions['right_text_answer'] = client_mysqldb.get_text_right_answers(dict_of_questions['id'])
        dict_of_questions['wrong_text_answers'] = [
            {'text': answer} for answer in client_mysqldb.get_text_answers_of_users(
                id_of_poll, dict_of_questions['serial_number']
            ) if answer != dict_of_questions['right_text_answer']]

    return dict_of_questions






