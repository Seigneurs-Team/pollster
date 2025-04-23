from Configs.Poll import (Poll, Question, Option, RightAnswer, RightTextAnswer)
from random import randint
from databases.mysql_db import check_the_type
from databases.mysql_db import client_mysqldb

import json


def get_random_id():
    return randint(1, 100000)


def set_poll(json_data: dict, id_of_author: int) -> tuple[Poll, list[Question], list[Option], list[RightAnswer], list[RightTextAnswer]]:
    assert json_data.get("name_of_poll", '') != ''
    assert json_data.get('tags', "") != ''
    assert isinstance(json_data.get('tags'), list)
    assert len(json_data.get('tags')) > 0

    poll: Poll = Poll(json_data.get("name_of_poll"), json_data.get("description", ''), json.dumps(json_data.get("tags"), ensure_ascii=False), get_random_id(), id_of_author, client_mysqldb.get_user_data_from_table(id_of_author)[0], None)
    list_of_questions: list[Question] = set_questions(json_data, poll)
    list_of_options: list[Option] = set_options(json_data, list_of_questions)
    list_of_right_answers: list[RightAnswer] = set_right_answers(json_data, list_of_questions)

    list_of_right_text_answers: list[RightTextAnswer] = set_right_text_answers(json_data, list_of_questions)

    return poll, list_of_questions, list_of_options, list_of_right_answers, list_of_right_text_answers


def set_questions(json_data: dict, poll_object: Poll) -> list[Question]:
    list_of_questions: list[Question] = []
    for question in json_data.get('questions', ''):
        check_the_type(question.get('type', ''))
        list_of_questions.append(
            Question(
                **poll_object.__dict__,
                id_of_question=get_random_id(),
                text_of_question=question.get('text', ''),
                type_of_question=question.get('type', ''),
                serial_number=question.get('id')
            )
        )
    return list_of_questions


def set_options(json_data: dict, question_object: list[Question]) -> list[Option]:
    list_of_options: list[Option] = []

    for index, question in enumerate(json_data.get('questions', '')):
        for option in question.get('options', ''):
            list_of_options.append(
                Option(
                    **question_object[index].__dict__,
                    id_of_option=get_random_id(),
                    option=option
                )
            )
    return list_of_options


def set_right_answers(json_data: dict, questions_object: list[Question]):
    list_of_right_answers: list[RightAnswer] = []
    for index, question in enumerate(json_data.get('questions', '')):
        for right_answer_id in question.get('rightAnswersId', ''):
            list_of_right_answers.append(
                RightAnswer(
                    **questions_object[index].__dict__,
                       RightAnswerId=right_answer_id
                )
            )
    return list_of_right_answers


def set_right_text_answers(json_data: dict, questions_object: list[Question]) -> list[RightTextAnswer]:
    list_of_right_text_answers: list[RightTextAnswer] = []

    for index, question in enumerate(json_data.get('questions', '')):
        right_text_answers = question.get("rightAnswer", '')
        list_of_right_text_answers.append(
            RightTextAnswer(
                **questions_object[index].__dict__,
                text_of_right_answer=right_text_answers
            )
        )

    return list_of_right_text_answers
