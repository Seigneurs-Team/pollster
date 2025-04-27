from Configs.Poll import Question, Option, RightAnswer, RightTextAnswer
import typing


def set_new_real_id(
        list_of_questions: list[Question],
        list_of_options: list[Option],
        list_of_right_answers: list[RightAnswer],
        list_of_right_text_answers: list[RightTextAnswer]
):
    list_of_options: list[Option] = change_id(list_of_questions, list_of_options)
    list_of_right_answers: list[RightAnswer] = change_id(list_of_questions, list_of_right_answers)

    list_of_right_text_answers: list[RightTextAnswer] = change_id(list_of_questions, list_of_right_text_answers)

    return list_of_options, list_of_right_answers, list_of_right_text_answers


def change_id(list_of_question: list[Question], list_of_object: list[typing.Union[Option, RightAnswer, RightTextAnswer]]):
    for index, question in enumerate(list_of_question):
        for index_, object_ in enumerate(list_of_object):
            if object_.serial_number == question.serial_number:
                list_of_object[index_].id_of_question = question.id_of_question

    return list_of_object