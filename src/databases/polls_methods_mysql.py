from databases.connection_shaker import get_connection_and_cursor, ConnectionAndCursor

from Configs.Poll import Poll, Question, Option, RightAnswer, RightTextAnswer
from Configs.Exceptions import NotFoundPoll
from app.create_poll_page.change_id import set_new_real_id
from PoW.generate_random_string import generate_random_string

import json
from typing import List
import mysql.connector
from logging import getLogger
import base64

logger = getLogger()


class PollsMethodsMySQL:
    @get_connection_and_cursor
    def get_metadata_of_poll(self, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(
            f"""SELECT name_of_poll, description, tags, id_of_author FROM polls WHERE id = {id_of_poll}""")
        return connection_object.cursor.fetchone()

    @get_connection_and_cursor
    def get_polls_tags(self, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        """
        Функция нужна для того, чтобы вернуть все теги опроса, которые представляют собой list[str]

        :param id_of_poll: идентификатор опроса
        :param connection_object:
        :return: list[str] - теги опроса
        """
        connection_object.cursor.execute(f"""SELECT tags FROM polls WHERE id = {id_of_poll}""")
        response_of_query = connection_object.cursor.fetchone()

        assert response_of_query is not None

        return json.loads(response_of_query[0])

    @get_connection_and_cursor
    def get_polls(self, num_of_polls: int = 4, only_for_user: bool = False, id_of_user: int = None,
                  connection_object: ConnectionAndCursor = None, main_page: bool = False) -> list:
        """
        Функция возвращает list, состоящий из id: int, tags: string, name_of_poll: string, description: string
        :param main_page:
        :param connection_object:
        :param num_of_polls: количество опросов, которые должна вернуть функция
        :param id_of_user: уникальный идентификатор пользователя
        :param only_for_user: bool значение, которое определяет - искать опросы для конкретного пользователя или нет
        :return: list
        """
        if only_for_user is False:
            if main_page:
                transaction = """SELECT name_of_poll, description, tags, id, id_of_author FROM polls
                    LEFT JOIN private_polls ON private_polls.id_of_poll = polls.id
                    WHERE private_polls.id_of_poll IS NULL"""
            else:
                transaction = """SELECT name_of_poll, description, tags, id, id_of_author FROM polls"""
                if id_of_user is not None:
                    transaction += f" WHERE id_of_author = {id_of_user}" if id_of_user is not None else ''
        else:
            transaction = f"""SELECT name_of_poll, description, tags, id, id_of_author FROM polls
                LEFT JOIN table_of_users_who_pass_the_poll ON table_of_users_who_pass_the_poll.id_of_poll = polls.id AND
                table_of_users_who_pass_the_poll.id_of_user = {id_of_user}
                LEFT JOIN private_polls ON polls.id = private_polls.id_of_poll
                WHERE table_of_users_who_pass_the_poll.id_of_poll IS NULL
                AND private_polls.id_of_poll IS NULL"""
        connection_object.cursor.execute(transaction)
        result = connection_object.cursor.fetchmany(num_of_polls)
        polls_list: list[Poll] = []
        for poll in result:
            cover = self.get_cover_of_poll_in_base64_format(poll[3], connection_object=connection_object)
            polls_list.append(Poll(poll[0], poll[1], json.loads(poll[2]), poll[3], id_of_user,
                                   self.get_user_data_from_table(poll[4])[0], cover))
        return polls_list

    @get_connection_and_cursor
    def get_polls_by_their_id(self, polls_id: list[int], connection_object: ConnectionAndCursor = None):
        polls_list: list = []
        for idx in polls_id:
            transaction = f"""SELECT name_of_poll, description, tags, id_of_author FROM polls WHERE id = {idx}"""
            connection_object.cursor.execute(transaction)
            result = connection_object.cursor.fetchone()

            if result is None:
                continue

            polls_list.append(Poll(result[0], result[1], json.loads(result[2]), idx, result[3],
                                   self.get_user_data_from_table(result[3])[0],
                                   self.get_cover_of_poll_in_base64_format(idx, connection_object=connection_object)))

        return polls_list

    def get_poll(self, id_of_poll: int) -> dict or None:
        """
        Функция выполняет транзакцию, у которой ответ состоит из перекрытия полей четырех таблиц.

        :param id_of_poll: идентификатор опроса
        :return: None
        """
        questions_entries = self.get_questions(id_of_poll)
        dict_of_poll = self.set_dict_poll(questions_entries, id_of_poll)
        return dict_of_poll

    def set_dict_poll(self, questions_entries: list, id_of_poll: int) -> dict:
        """
        Функция нужна для создания словаря опроса для отправки JSON клиенту

        :param questions_entries: записи вопросов связанных с опросом

        :param id_of_poll: идентификатор опроса

        :return: словарь состоящий из списков вопросов, описания опроса, названия опроса и тегов
        """
        cover = self.get_cover_of_poll_in_base64_format(id_of_poll)
        dict_of_poll: dict = {
            'id_of_poll': id_of_poll,
            'name_of_poll': questions_entries[0][1],
            'description': questions_entries[0][3],
            'tags': json.loads(questions_entries[0][2]),
            'cover': cover,
            'questions': []
        }

        for index, question in enumerate(questions_entries):
            id_of_question = question[4]
            type_of_question = question[5]
            text_of_question = question[6]
            serial_number = question[7]

            dict_of_poll['questions'].append({
                'id': serial_number,
                'type': type_of_question,
                'text': text_of_question
            })

            if type_of_question == 'short text':
                dict_of_poll['questions'][index]['shortTextRightAnswer'] = self.get_text_right_answers(id_of_question)

            elif type_of_question == 'radio' or type_of_question == 'checkbox':
                dict_of_poll['questions'][index]['options'] = self.get_options(id_of_question)
                dict_of_poll['questions'][index]['rightAnswersId'] = self.get_right_answers(id_of_question)
        return dict_of_poll

    @get_connection_and_cursor
    def get_questions(self, id_of_poll: int, connection_object: ConnectionAndCursor = None) -> List or None:
        """
        Функция возвращает вопросы связанные с конкретным опросом по его id

        :param connection_object:
        :param id_of_poll: идентификатор опроса

        :return: список вопросов
        """
        connection_object.cursor.execute(f"""SELECT polls.id, polls.name_of_poll, polls.tags, 
                     polls.description, questions.id_of_question, questions.type_of_question, questions.text_of_question,
                     questions.serial_number
                     FROM polls INNER JOIN questions ON polls.id = questions.id_of_poll
                     WHERE polls.id = {id_of_poll}""")
        response_from_query = connection_object.cursor.fetchall()

        if len(response_from_query) == 0:
            raise NotFoundPoll('Опрос не найден')
        return response_from_query

    @get_connection_and_cursor
    def get_options(self, id_of_question: int, connection_object: ConnectionAndCursor = None) -> list[str]:
        """
        Функция выполняет выборку записей из таблицы options по ключевому ключу id_of_question
        :param connection_object:
        :param id_of_question: идентификатор вопроса
        :return: возвращает список объекта Option
        """
        connection_object.cursor.execute(f"""SELECT option_name FROM options WHERE id_of_question = {id_of_question}""")
        response_from_query = connection_object.cursor.fetchall()

        return [option[0] for option in response_from_query]

    @get_connection_and_cursor
    def get_text_right_answers(self, id_of_question: int, connection_object: ConnectionAndCursor = None) -> str:
        """
        Функция выполняет выборку записей из таблицы text_rights_answers по ключевому ключу id_of_question
        :param connection_object:
        :param id_of_question: идентификатор вопроса
        :return: возвращает список объекта RightTextAnswer
        """
        connection_object.cursor.execute(
            f"""SELECT text_of_right_answer FROM text_rights_answers WHERE id_of_question = {id_of_question}""")
        response_of_query = connection_object.cursor.fetchone()

        if response_of_query is None:
            return ''

        return response_of_query[0]

    @get_connection_and_cursor
    def get_right_answers(self, id_of_question: int, connection_object: ConnectionAndCursor = None):
        """
        Функция выполняет выборку записей из таблицы rightAnswers по ключевому ключу id_of_question
        :return:
        """

        connection_object.cursor.execute(
            f"""SELECT rightAnswerId FROM rightAnswers WHERE id_of_question={id_of_question}""")
        response_of_query = connection_object.cursor.fetchall()

        return [right_answer_id[0] for right_answer_id in response_of_query]

    @get_connection_and_cursor
    def create_pool(
            self,
            poll: Poll,
            list_of_questions: list[Question],
            list_of_options: list[Option],
            list_of_right_answers: list[RightAnswer],
            list_of_text_right_answers: list[RightTextAnswer],
            connection_object: ConnectionAndCursor = None
    ) -> (bool, Poll) or (bool, None):
        """
        Функция создает опрос в базе данных
        :param connection_object:
        :param poll: объект класса Poll
        :param list_of_questions: объект класса list[Question]
        :param list_of_options: объект класса list[Option]
        :param list_of_right_answers: объект класса list[RightAnswer]
        :param list_of_text_right_answers: объект класса list[RightTextAnswer]
        :return: возвращает 1 или 0; 1 означает success create poll, 0 означает, что транзакция не была совершена
        """
        try:
            id_of_poll = self.add_new_entry_into_polls_table(poll, connection_object=connection_object)
            poll.id_of_poll = id_of_poll
            for index, question in enumerate(list_of_questions):
                id_of_question = self.add_new_entry_into_questions_table(question, id_of_poll,
                                                                         connection_object=connection_object)
                list_of_questions[index].id_of_question = id_of_question

            list_of_options, list_of_right_answers, list_of_text_right_answers = set_new_real_id(
                list_of_questions, list_of_options,
                list_of_right_answers, list_of_text_right_answers)

            for index, option in enumerate(list_of_options):
                self.add_new_entry_into_options_table(option, connection_object=connection_object)

            for index, right_answer in enumerate(list_of_right_answers):
                self.add_new_entry_into_right_answers_table(right_answer, connection_object=connection_object)
            for right_text_answer in list_of_text_right_answers:
                self.add_new_entry_into_text_rights_answers_table(right_text_answer,
                                                                  connection_object=connection_object)
            connection_object.connection.commit()
            return True, poll
        except Exception as ex:
            logger.warning('Транзакция не была успешно выполнена. Опрос не был создан', exc_info=ex)
            return False, None

    @get_connection_and_cursor
    def add_new_entry_into_polls_table(self, poll: Poll, connection_object: ConnectionAndCursor = None) -> int:
        """
        Добавляет запись в таблицу polls
        :param connection_object:
        :param poll: объект класса Poll
        :return:
        """
        connection_object.cursor.execute(
            """INSERT INTO polls(tags, name_of_poll, description, id_of_author) VALUES (%s, %s, %s, %s)""",
            (poll.tags, poll.name_of_poll, poll.description, poll.id_of_author))
        connection_object.cursor.execute("""SELECT LAST_INSERT_ID()""")
        id_of_poll = connection_object.cursor.fetchone()[0]
        return id_of_poll

    @get_connection_and_cursor
    def add_new_entry_into_questions_table(self, question: Question, id_of_poll: int,
                                           connection_object: ConnectionAndCursor = None) -> int:
        """
        Добавляет запись в таблицу questions
        :param id_of_poll:
        :param connection_object:
        :param question: объект класса Question
        :return:
        """
        question.id_of_poll = id_of_poll
        connection_object.cursor.execute(
            """INSERT INTO questions(id_of_poll, text_of_question, type_of_question, serial_number) VALUES (%s, %s, %s, %s)""",
            (question.id_of_poll, question.text_of_question, question.type_of_question, question.serial_number))
        connection_object.cursor.execute("""SELECT LAST_INSERT_ID()""")
        id_of_question = connection_object.cursor.fetchone()[0]

        return id_of_question

    @get_connection_and_cursor
    def add_new_entry_into_options_table(self, option: Option, connection_object: ConnectionAndCursor = None) -> None:
        """
        Добавляет запись в таблицу options
        :param connection_object:
        :param option: объект класса Option
        :return:
        """
        connection_object.cursor.execute("""INSERT INTO options(id_of_question, option_name) VALUES (%s, %s)""",
                                         (option.id_of_question, option.option))

    @get_connection_and_cursor
    def add_new_entry_into_right_answers_table(self, right_answer: RightAnswer,
                                               connection_object: ConnectionAndCursor = None) -> None:
        """
        Добавляет запись в таблицу rightAnswers
        :param connection_object:
        :param right_answer: объект класса RightAnswer
        :return:
        """
        connection_object.cursor.execute("""INSERT INTO rightAnswers(id_of_question, rightAnswerId) VALUES (%s, %s)""",
                                         (right_answer.id_of_question, right_answer.RightAnswerId))

    @get_connection_and_cursor
    def add_new_entry_into_text_rights_answers_table(self, right_text_answer: RightTextAnswer,
                                                     connection_object: ConnectionAndCursor = None) -> None:
        """
        Добавляет запись в таблицу text_rights_answers
        :param connection_object:
        :param right_text_answer: объект класса RightTextAnswer
        :return:
        """
        connection_object.cursor.execute(
            """INSERT INTO text_rights_answers(id_of_question, text_of_right_answer) VALUES(%s, %s)""",
            (right_text_answer.id_of_question, right_text_answer.text_of_right_answer))

    @get_connection_and_cursor
    def set_types_of_questions(self, connection_object: ConnectionAndCursor = None):
        """
        Функция добавляет в БД записи о типах вопросов, если их нет в БД.

        :return: None
        """
        connection_object.cursor.execute("""SELECT id FROM types_of_question""")
        types_of_question = ['long text', 'short text', 'radio', 'checkbox']
        if connection_object.cursor.fetchone() is None:
            for i, type_of_question in enumerate(types_of_question):
                connection_object.cursor.execute("""INSERT INTO types_of_question(id, type) VALUES (%s, %s)""",
                                                 (i, type_of_question))
                connection_object.connection.commit()
        else:
            return None

    @get_connection_and_cursor
    def get_types_of_question(self, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает типы вопросов из БД

        :return: список типов list[str]
        """
        connection_object.cursor.execute("""SELECT type FROM types_of_question""")
        result = connection_object.cursor.fetchall()
        return [type_of_question[0] for type_of_question in result]

    @get_connection_and_cursor
    def get_id_of_author_of_poll(self, id_of_poll, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает идентификатор автора опроса по конкретному идентификатору опроса

        :param connection_object:
        :param id_of_poll: идентификатор опроса
        :return: идентификатор автора
        """
        connection_object.cursor.execute(f"""SELECT id_of_author FROM polls WHERE id={id_of_poll}""")
        data_of_query = connection_object.cursor.fetchone()
        if data_of_query is None:
            raise NotFoundPoll('Не найден опрос с данным id')

        return data_of_query[0]

    @get_connection_and_cursor
    def delete_poll(self, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        """
        Функция удаляет опрос из БД
        :param connection_object:
        :param id_of_poll: идентификатор опроса
        :return:
        """
        connection_object.cursor.execute(f"""DELETE FROM polls WHERE id={id_of_poll}""")
        connection_object.connection.commit()

    @get_connection_and_cursor
    def create_entry_into_ranking_table(self, id_of_poll: int, vector_of_poll: bytes,
                                        connection_object: ConnectionAndCursor = None):
        """
        Функция создает запись в ranking_table. Запись представляет собой идентификатор опроса и вектор тегов,
        представленный в виде байтов

        :param connection_object:
        :param id_of_poll: идентификатор опроса
        :param vector_of_poll: поток байтов вектора тегов опроса
        :return: None
        """
        connection_object.cursor.execute("""INSERT INTO ranking_table(id_of_poll, vector_of_poll) VALUES(%s, %s)""",
                                         (id_of_poll, vector_of_poll))
        connection_object.connection.commit()

    @get_connection_and_cursor
    def get_vectorization_polls(self, id_of_user: int, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает идентификаторы опросов и векторизованные теги опросов, которые не были пройдены пользователем

        :param connection_object:
        :param id_of_user: идентификатор пользователя

        :return: идентификатор опроса и вектор тегов в байтовом представлении
        """
        connection_object.cursor.execute(f"""SELECT ranking_table.id_of_poll, ranking_table.vector_of_poll
            FROM ranking_table LEFT JOIN table_of_users_who_pass_the_poll 
            ON ranking_table.id_of_poll = table_of_users_who_pass_the_poll.id_of_poll AND
            table_of_users_who_pass_the_poll.id_of_user = {id_of_user}
            LEFT JOIN private_polls ON private_polls.id_of_poll = ranking_table.id_of_poll
            WHERE table_of_users_who_pass_the_poll.id_of_poll IS NULL
            AND private_polls.id_of_poll is NULL""")

        response_of_query = connection_object.cursor.fetchall()

        assert len(response_of_query) != 0

        return response_of_query

    @get_connection_and_cursor
    def get_count_of_text_answers(self, id_of_poll: int, serial_number: int, type_of_question,
                                  connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT COUNT(*) FROM data_of_passing_poll_from_user WHERE
             id_of_poll = {id_of_poll} AND serial_number_of_question = {serial_number} AND type_of_question = "{type_of_question}" """)

        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def get_count_of_right_answers(self, id_of_poll: int, serial_number: int,
                                   connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT COUNT(*) FROM data_of_passing_poll_from_user INNER JOIN text_rights_answers ON 
            text_rights_answers.text_of_right_answer = data_of_passing_poll_from_user.value
            WHERE data_of_passing_poll_from_user.id_of_poll = {id_of_poll} 
            AND data_of_passing_poll_from_user.type_of_question = "short text"
            AND data_of_passing_poll_from_user.serial_number_of_question = {serial_number}""")

        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def get_count_of_wrong_answers(self, id_of_poll: int, serial_number: int,
                                   connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT COUNT(*) FROM data_of_passing_poll_from_user LEFT JOIN text_rights_answers 
            ON text_rights_answers.text_of_right_answer = data_of_passing_poll_from_user.value
            WHERE data_of_passing_poll_from_user.id_of_poll = {id_of_poll} 
            AND data_of_passing_poll_from_user.type_of_question = "short text"
            AND data_of_passing_poll_from_user.serial_number_of_question = {serial_number}
            AND text_rights_answers.id_of_question IS NULL""")

        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def add_entry_into_private_polls(self, id_of_poll: int, connection_object: ConnectionAndCursor = None) -> str:
        try:
            code = generate_random_string(15)
            connection_object.cursor.execute("""INSERT INTO private_polls(id_of_poll, code) VALUES (%s, %s)""",
                                             (id_of_poll, code))
            connection_object.connection.commit()
            return code
        except mysql.connector.IntegrityError:
            self.add_entry_into_private_polls(id_of_poll, connection_object=connection_object)

    @get_connection_and_cursor
    def get_id_of_private_poll(self, code: str, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT id_of_poll FROM private_polls WHERE code = "{code}" """)
        response = connection_object.cursor.fetchone()[0]

        return response

    @get_connection_and_cursor
    def get_id_of_private_polls(self, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT id_of_poll FROM private_polls""")
        response = [private_poll[0] for private_poll in connection_object.cursor.fetchall()]

        return response

    @get_connection_and_cursor
    def check_poll_on_private(self, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"SELECT COUNT(*) FROM private_polls WHERE id_of_poll = {id_of_poll}")
        response = connection_object.cursor.fetchone()
        return True if response[0] == 1 else False

    @get_connection_and_cursor
    def get_code_from_private_polls(self, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT code FROM private_polls WHERE id_of_poll = {id_of_poll}""")
        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def add_cover_into_cover_of_polls(self, id_of_poll: int, cover: bytes,
                                      connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute("""INSERT INTO cover_of_polls(cover, id_of_poll) VALUES (%s, %s)""",
                                         (cover, id_of_poll))
        connection_object.connection.commit()

    @get_connection_and_cursor
    def get_cover_of_poll_in_base64_format(self, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT cover FROM cover_of_polls WHERE id_of_poll = {id_of_poll}""")
        response_of_query = connection_object.cursor.fetchone()
        if response_of_query is not None:
            cover = base64.b64encode(response_of_query[0]).decode()
            return cover
        else:
            return None