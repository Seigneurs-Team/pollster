import base64
import dataclasses
import datetime
import json
import random
import typing

from mysql.connector import connect, pooling
import mysql
import logging
from Configs.Hosts import Hosts
from Configs.Poll import (
    Poll,
    Question,
    Option,
    RightAnswer,
    RightTextAnswer
)
from app.create_poll_page.random_id import get_random_id
from typing import List

from Configs.Exceptions import NotFoundPoll, ErrorSameLogins, NotFoundCookieIntoPowTable, CookieWasExpired, RepeatPollError, TryToXSS
from PoW.generate_random_string import generate_random_string
logger = logging.getLogger()


def check_the_type(type_of_question: str):
    """
    Проверка значений поля type на несоответствие со значениями из БД.
    :param type_of_question: тип вопроса
    :return: None
    """
    types = client_mysqldb.get_types_of_question()
    if type_of_question not in types:
        raise TryToXSS("попытка XSS атаки")


@dataclasses.dataclass
class ConnectionAndCursor:
    connection: mysql.connector.pooling.MySQLConnectionPool
    cursor: mysql.connector.connection.MySQLCursor


def get_connection_and_cursor(func):
    def wrapped_func(*args, **kwargs):
        if 'connection_object' not in kwargs:
            connection = args[0].database_pool.get_connection()
            cursor = connection.cursor(buffered=True)
            try:
                connection_object = ConnectionAndCursor(connection, cursor)
                kwargs['connection_object'] = connection_object
                response = func(*args, **kwargs)
            finally:
                connection.close()
                cursor.close()
            return response
        else:
            return func(*args, **kwargs)

    return wrapped_func


class MysqlDB:
    def __init__(self):
        self.database_pool = self.connect_to_db()
        self.create_table()

    def connect_to_db(self):
        try:
            database_pool = pooling.MySQLConnectionPool(
                host=Hosts.mysql_db,
                user='root',
                password='root1234567890',
                auth_plugin='mysql_native_password',
                database='Pollster_DB',
                pool_size=10,
                pool_reset_session=True
            )
            logger.info('Успешное подключение')
            return database_pool
        except (mysql.connector.errors.ProgrammingError, mysql.connector.errors.DatabaseError):
            try:
                database_pool = pooling.MySQLConnectionPool(
                    host=Hosts.mysql_db,
                    user='root',
                    password='root1234567890',
                    auth_plugin='mysql_native_password',
                    pool_size=10,
                    pool_reset_session=True
                )
                connection = database_pool.get_connection()
                cursor = connection.cursor()

                cursor.execute('CREATE DATABASE Pollster_DB')
                connection.commit()

                connection.close()
                cursor.close()
                self.connect_to_db()
            except (mysql.connector.errors.ProgrammingError, mysql.connector.errors.DatabaseError):
                self.connect_to_db()

    @get_connection_and_cursor
    def create_table(self, connection_object: ConnectionAndCursor = None):
        #polls
        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS polls(id INT UNSIGNED, tags VARCHAR(100), name_of_poll VARCHAR(100), description TEXT, id_of_author INT, PRIMARY KEY (id))""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS questions(id_of_question INT UNSIGNED, 
        id_of_poll INT UNSIGNED, text_of_question VARCHAR(100), type_of_question VARCHAR(50), serial_number INT,
        PRIMARY KEY (id_of_question),
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS options(id_of_option INT UNSIGNED PRIMARY KEY, id_of_question INT UNSIGNED, 
        option_name VARCHAR(100),
        FOREIGN KEY (id_of_question) REFERENCES questions (id_of_question) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS rightAnswers(id_of_question INT UNSIGNED, rightAnswerId INT UNSIGNED, 
        PRIMARY KEY (id_of_question, rightAnswerId), FOREIGN KEY (id_of_question) REFERENCES questions (id_of_question) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS text_rights_answers(id_of_question INT UNSIGNED, text_of_right_answer TEXT, 
        PRIMARY KEY (id_of_question), FOREIGN KEY (id_of_question) REFERENCES questions (id_of_question) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS types_of_question(id INT, type VARCHAR(50), PRIMARY KEY (id))""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS ranking_table(id_of_poll INT UNSIGNED, vector_of_poll BLOB, 
        PRIMARY KEY (id_of_poll), 
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS private_polls(id_of_poll INT UNSIGNED, code VARCHAR(15) UNIQUE,
        PRIMARY KEY (id_of_poll), 
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS cover_of_polls(cover BLOB, id_of_poll INT UNSIGNED PRIMARY KEY,
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")

        #users
        #id_of_user состоит из последовательности длинной 6 цифр со знаком минус
        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS table_of_type_of_users(id_of_type INT, type VARCHAR(100), PRIMARY KEY (id_of_type))""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS users(id_of_user INT PRIMARY KEY, type_of_user INT, 
        FOREIGN KEY (type_of_user) REFERENCES table_of_type_of_users(id_of_type) ON UPDATE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS user(id_of_user INT, password VARCHAR(255), login VARCHAR(100), nickname VARCHAR(50), tags VARCHAR(100), date_of_birth DATE, number_of_phone VARCHAR(17),
        PRIMARY KEY (id_of_user), 
        FOREIGN KEY (id_of_user) REFERENCES users(id_of_user) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS sessions(id_of_user INT, id_of_cookie INT, cookie VARCHAR(10), expired TIMESTAMP, name_of_cookie VARCHAR(30), 
        PRIMARY KEY (id_of_cookie), 
        FOREIGN KEY (id_of_user) REFERENCES users (id_of_user) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS pow_table(pow INT, cookie VARCHAR(10))""")
        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS ranking_table_of_users(id_of_user INT PRIMARY KEY, vector_of_user BLOB,
        FOREIGN KEY (id_of_user) REFERENCES users (id_of_user) ON DELETE CASCADE)""")

        #superuser
        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS superusers(id_of_superuser INT, login VARCHAR(100), password VARCHAR(255), 
        PRIMARY KEY (id_of_superuser), 
        FOREIGN KEY (id_of_superuser) REFERENCES users (id_of_user) ON DELETE CASCADE)""")
        #данные, которые пользователь ввел в ответах на опрос
        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS table_of_users_who_pass_the_poll(id_of_user INT, id_of_poll INT UNSIGNED, 
        PRIMARY KEY (id_of_user, id_of_poll), 
        FOREIGN KEY (id_of_user) REFERENCES users (id_of_user) ON DELETE CASCADE, 
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")
        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS data_of_passing_poll_from_user(id INT AUTO_INCREMENT, id_of_poll INT UNSIGNED, id_of_user INT, serial_number_of_question INT, type_of_question VARCHAR(50), value TEXT, PRIMARY KEY (id))""")
        connection_object.connection.commit()

        self.set_types_of_questions()
        self.set_table_type_of_users()

#-----------------------------------------------------------------------------------------------------------------------
# часть кода связанная с созданием, редактированием и удалением опросов
    @get_connection_and_cursor
    def get_metadata_of_poll(self, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT name_of_poll, description, tags, id_of_author FROM polls WHERE id = {id_of_poll}""")
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
    def get_polls(self, num_of_polls: int = 4, only_for_user: bool = False, id_of_user: int = None, connection_object: ConnectionAndCursor = None, main_page: bool = False) -> list:
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
            polls_list.append(Poll(poll[0], poll[1], json.loads(poll[2]), poll[3], id_of_user, client_mysqldb.get_user_data_from_table(poll[4])[0], cover))
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

            polls_list.append(Poll(result[0], result[1], json.loads(result[2]), idx, result[3], client_mysqldb.get_user_data_from_table(result[3])[0], self.get_cover_of_poll_in_base64_format(idx, connection_object=connection_object)))

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
        connection_object.cursor.execute(f"""SELECT text_of_right_answer FROM text_rights_answers WHERE id_of_question = {id_of_question}""")
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

        connection_object.cursor.execute(f"""SELECT rightAnswerId FROM rightAnswers WHERE id_of_question={id_of_question}""")
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
    ) -> bool:
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
            self.add_new_entry_into_polls_table(poll, connection_object=connection_object)
            for question in list_of_questions:
                self.add_new_entry_into_questions_table(question, connection_object=connection_object)

            for option in list_of_options:
                self.add_new_entry_into_options_table(option, connection_object=connection_object)

            for right_answer in list_of_right_answers:
                self.add_new_entry_into_right_answers_table(right_answer, connection_object=connection_object)
            for right_text_answer in list_of_text_right_answers:
                self.add_new_entry_into_text_rights_answers_table(right_text_answer, connection_object=connection_object)
            connection_object.connection.commit()
            return True
        except Exception as ex:
            logger.warning('Транзакция не была успешно выполнена. Опрос не был создан', exc_info=ex)
            return False

    @get_connection_and_cursor
    def add_new_entry_into_polls_table(self, poll: Poll, connection_object: ConnectionAndCursor = None) -> None:
        """
        Добавляет запись в таблицу polls
        :param connection_object:
        :param poll: объект класса Poll
        :return:
        """
        try:
            connection_object.cursor.execute("""INSERT INTO polls(id, tags, name_of_poll, description, id_of_author) VALUES (%s, %s, %s, %s, %s)""",
                                             (poll.id_of_poll, poll.tags, poll.name_of_poll, poll.description, poll.id_of_author))
        except mysql.connector.errors.IntegrityError:
            poll.id_of_poll = get_random_id()
            self.add_new_entry_into_polls_table(poll)

    @get_connection_and_cursor
    def add_new_entry_into_questions_table(self, question: Question, connection_object: ConnectionAndCursor = None) -> None:
        """
        Добавляет запись в таблицу questions
        :param connection_object:
        :param question: объект класса Question
        :return:
        """
        try:
            connection_object.cursor.execute("""INSERT INTO questions(id_of_question, id_of_poll, text_of_question, type_of_question, serial_number) VALUES (%s, %s, %s, %s, %s)""",
                                             (question.id_of_question, question.id_of_poll, question.text_of_question, question.type_of_question, question.serial_number))
        except mysql.connector.errors.IntegrityError:
            question.id_of_question = get_random_id()
            self.add_new_entry_into_questions_table(question)

    @get_connection_and_cursor
    def add_new_entry_into_options_table(self, option: Option, connection_object: ConnectionAndCursor = None) -> None:
        """
        Добавляет запись в таблицу options
        :param connection_object:
        :param option: объект класса Option
        :return:
        """
        try:
            connection_object.cursor.execute("""INSERT INTO options(id_of_option, id_of_question, option_name) VALUES (%s, %s, %s)""",
                                             (option.id_of_option, option.id_of_question, option.option))
        except mysql.connector.errors.IntegrityError:
            option.id_of_option = get_random_id()
            self.add_new_entry_into_options_table(option)

    @get_connection_and_cursor
    def add_new_entry_into_right_answers_table(self, right_answer: RightAnswer, connection_object: ConnectionAndCursor = None) -> None:
        """
        Добавляет запись в таблицу rightAnswers
        :param connection_object:
        :param right_answer: объект класса RightAnswer
        :return:
        """
        connection_object.cursor.execute("""INSERT INTO rightAnswers(id_of_question, rightAnswerId) VALUES (%s, %s)""",
                                         (right_answer.id_of_question, right_answer.RightAnswerId))

    @get_connection_and_cursor
    def add_new_entry_into_text_rights_answers_table(self, right_text_answer: RightTextAnswer, connection_object: ConnectionAndCursor = None) -> None:
        """
        Добавляет запись в таблицу text_rights_answers
        :param connection_object:
        :param right_text_answer: объект класса RightTextAnswer
        :return:
        """
        connection_object.cursor.execute("""INSERT INTO text_rights_answers(id_of_question, text_of_right_answer) VALUES(%s, %s)""",
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
                connection_object.cursor.execute("""INSERT INTO types_of_question(id, type) VALUES (%s, %s)""", (i, type_of_question))
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
    def create_entry_into_ranking_table(self, id_of_poll: int, vector_of_poll: bytes, connection_object: ConnectionAndCursor = None):
        """
        Функция создает запись в ranking_table. Запись представляет собой идентификатор опроса и вектор тегов,
        представленный в виде байтов

        :param connection_object:
        :param id_of_poll: идентификатор опроса
        :param vector_of_poll: поток байтов вектора тегов опроса
        :return: None
        """
        connection_object.cursor.execute("""INSERT INTO ranking_table(id_of_poll, vector_of_poll) VALUES(%s, %s)""", (id_of_poll, vector_of_poll))
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
    def get_count_of_text_answers(self, id_of_poll: int, serial_number: int, type_of_question, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT COUNT(*) FROM data_of_passing_poll_from_user WHERE
         id_of_poll = {id_of_poll} AND serial_number_of_question = {serial_number} AND type_of_question = "{type_of_question}" """)

        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def get_count_of_right_answers(self, id_of_poll: int, serial_number: int, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""SELECT COUNT(*) FROM data_of_passing_poll_from_user INNER JOIN text_rights_answers ON 
        text_rights_answers.text_of_right_answer = data_of_passing_poll_from_user.value
        WHERE data_of_passing_poll_from_user.id_of_poll = {id_of_poll} 
        AND data_of_passing_poll_from_user.type_of_question = "short text"
        AND data_of_passing_poll_from_user.serial_number_of_question = {serial_number}""")

        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def get_count_of_wrong_answers(self, id_of_poll: int, serial_number: int, connection_object: ConnectionAndCursor = None):
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
            connection_object.cursor.execute("""INSERT INTO private_polls(id_of_poll, code) VALUES (%s, %s)""", (id_of_poll, code))
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
    def add_cover_into_cover_of_polls(self, id_of_poll: int, cover: bytes, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute("""INSERT INTO cover_of_polls(cover, id_of_poll) VALUES (%s, %s)""", (cover, id_of_poll))
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

#-----------------------------------------------------------------------------------------------------------------------
# часть кода связанная с методами базы данных: подключение, переподключение, удаление таблиц
    @get_connection_and_cursor
    def delete_tables(self, connection_object: ConnectionAndCursor = None):
        """
        Функция нужна для удаления таблиц в БД

        :return: None
        """
        connection_object.cursor.execute("""DROP TABLE polls, questions, options, rightAnswers""")
        connection_object.connection.commit()

    #-----------------------------------------------------------------------------------------------------------------------
# часть кода связанная с методами пользователей

    @get_connection_and_cursor
    def set_table_type_of_users(self, connection_object: ConnectionAndCursor = None):
        """
        Функция нужна для добавления в БД типов пользователей: user, staff

        :return: None
        """
        connection_object.cursor.execute("""SELECT type FROM table_of_type_of_users""")
        if connection_object.cursor.fetchone() is None:
            connection_object.cursor.execute("""INSERT INTO table_of_type_of_users(id_of_type, type) VALUES(%s, %s)""", (1, 'user'))
            connection_object.cursor.execute("""INSERT INTO table_of_type_of_users(id_of_type, type) VALUES(%s, %s)""", (2, 'staff'))
            connection_object.connection.commit()

    @get_connection_and_cursor
    def create_superuser(self, connection_object: ConnectionAndCursor = None):
        """
        Функция создает суперпользователя ака админ

        :return: None
        """
        try:
            id_of_superuser = random.randint(-99999999, -9999999)
            connection_object.cursor.execute("""INSERT INTO users (id_of_user, type_of_user) VALUES (%s, %s)""", (id_of_superuser, 3))
            connection_object.cursor.execute("""INSERT INTO superusers (id_of_superusers, login, password) VALUES (%s, %s, %s)""", (id_of_superuser, 'admin', 'P@ssw0rd'))
            connection_object.connection.commit()
        except mysql.connector.IntegrityError:
            self.create_superuser()

    @get_connection_and_cursor
    def create_user(self, login: str, password: str, type_of_user: int, nickname: str, connection_object: ConnectionAndCursor = None):
        """
        Функция создает пользователя в БД. Также есть проверка на то, что пользователь уже существует в БД с таким логином
        :param connection_object:
        :param login: логин
        :param password: пароль
        :param type_of_user: тип пользователя (user, staff)
        :param nickname: никнейм
        :return: None
        """
        connection_object.cursor.execute(f"""SELECT * FROM user WHERE login = "{login}" OR nickname = "{nickname}" """)
        if len(connection_object.cursor.fetchall()) != 0:
            raise ErrorSameLogins('одинаковый логин')
        try:
            id_of_user = random.randint(-9999999, -999999)
            connection_object.cursor.execute("""INSERT INTO users (id_of_user, type_of_user) VALUES (%s, %s)""", (id_of_user, type_of_user))
            connection_object.cursor.execute("""INSERT INTO user (id_of_user, login, password, nickname) VALUES (%s, %s, %s, %s)""", (id_of_user, login, password, nickname))
            connection_object.connection.commit()
        except mysql.connector.IntegrityError:
            self.create_user(login, password, type_of_user, nickname)

    @get_connection_and_cursor
    def get_user_password_and_id_of_user_from_table(self, login, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает пароль и идентификатор пользователя по логину

        :param connection_object:
        :param login: логин

        :return: пароль и идентификатор пользователя
        """
        connection_object.cursor.execute(f"""SELECT password, id_of_user FROM user WHERE login = "{login}" """)
        response = connection_object.cursor.fetchone()
        if response is None:
            return None, None
        else:
            return response[0], response[1]

    @get_connection_and_cursor
    def get_user_nickname_from_table_with_cookie(self, cookie: str, name_of_cookie: str, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает никнейм пользователя по куки. Также в функции присутствует механизм проверки смерти куки.

        :param connection_object:
        :param cookie: куки значение

        :param name_of_cookie: куки название

        :return: никнейм пользователя
        """
        connection_object.cursor.execute(f"""SELECT expired, id_of_user FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" """)
        session = connection_object.cursor.fetchone()
        now = datetime.datetime.now()

        assert session is not None

        if now < session[0]:
            connection_object.cursor.execute(f"""SELECT nickname FROM user WHERE id_of_user = {session[1]}""")
            user = connection_object.cursor.fetchone()
            if user is not None:
                return user[0]
            return None

        else:
            self.delete_cookie_from_session_table(cookie, name_of_cookie, session[1])
            raise CookieWasExpired("время жизни куки файлов кончилось")

    @get_connection_and_cursor
    def get_id_of_user_from_table_with_cookies(self, cookie: str, name_of_cookie: str, connection_object: ConnectionAndCursor = None) -> str:
        """
        Функция возвращает идентификатор пользователя по куки из таблицы sessions
        :param connection_object:
        :param cookie: куки значение
        :param name_of_cookie: имя куки
        :return: идентификатор пользователя
        """
        connection_object.cursor.execute(f"""SELECT id_of_user FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" """)
        session = connection_object.cursor.fetchone()
        assert session is not None
        return session[0]

    @get_connection_and_cursor
    def get_user_data_from_table(self, id_of_user: int, connection_object: ConnectionAndCursor = None) -> tuple:
        """
        Функция нужна для выборки данных пользователя из таблицы

        :param connection_object:
        :param id_of_user: идентификатор пользователя

        :return: tuple состоящий из никнейма, номера телефона, даты рождения и тегов
        """
        connection_object.cursor.execute(f"""SELECT nickname, login, number_of_phone, date_of_birth, tags FROM user WHERE id_of_user={id_of_user}""")
        return connection_object.cursor.fetchone()

    @get_connection_and_cursor
    def create_cookie_into_pow_table(self, cookie: str, connection_object: ConnectionAndCursor = None):
        """
        Функция создает запись в таблице pow_table
        :param connection_object:
        :param cookie:
        :return: None
        """
        try:
            connection_object.cursor.execute("""INSERT INTO pow_table (cookie) VALUES (%s)""", (cookie,))
            connection_object.connection.commit()
        except mysql.connector.IntegrityError:
            raise Exception

    @get_connection_and_cursor
    def update_pow_in_pow_table(self, cookie: str, pow: int, connection_object: ConnectionAndCursor = None):
        """
        Функция обновляет запись в таблице pow_table
        :param connection_object:
        :param cookie:
        :param pow:
        :return: None
        """
        connection_object.cursor.execute(f"""UPDATE pow_table SET pow = {pow} WHERE cookie = "{cookie}" """)
        connection_object.connection.commit()

    @get_connection_and_cursor
    def get_pow(self, cookie: str, connection_object: ConnectionAndCursor = None):
        """
        Функция нудна для получения pow значения из таблицы pow_table по куки
        :param connection_object:
        :param cookie: куки
        :return: None
        """
        connection_object.cursor.execute(f"""SELECT pow FROM pow_table WHERE cookie = "{cookie}" """)
        response = connection_object.cursor.fetchall()
        if len(response) != 0:
            return response[0][0]
        else:
            raise NotFoundCookieIntoPowTable('не найден куки в таблице')

    @get_connection_and_cursor
    def create_cookie_into_session_table(self, cookie: str, name_of_cookie: str, id_of_user: int, expired: datetime.datetime, connection_object: ConnectionAndCursor = None):
        """
        Функция нужна для создания сессии клиента в системе
        :param connection_object:
        :param cookie: куки
        :param name_of_cookie: название куки
        :param id_of_user: идентификатор пользователя
        :param expired: время жизни куки
        :return: None
        """
        try:
            connection_object.cursor.execute(f"""SELECT id_of_cookie FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" """)
            if connection_object.cursor.fetchone() is not None:
                raise Exception

            connection_object.cursor.execute(f"""INSERT INTO sessions (id_of_user, cookie, name_of_cookie, expired, id_of_cookie) VALUES (%s, %s, %s, %s, %s)""", (id_of_user, cookie, name_of_cookie, expired, random.randint(0, 10 ** 4)))
            connection_object.connection.commit()

        except mysql.connector.IntegrityError:
            self.create_cookie_into_session_table(cookie, name_of_cookie, id_of_user, expired)
        except Exception:
            new_cookie = generate_random_string(10)
            self.create_cookie_into_session_table(new_cookie, name_of_cookie, id_of_user, expired)

    @get_connection_and_cursor
    def delete_cookie_from_session_table(self, cookie: str, name_of_cookie: str, id_of_user: int, connection_object: ConnectionAndCursor = None):
        """
        Удаление записи в sessions
        :param connection_object:
        :param cookie: значение куки
        :param name_of_cookie: название куки
        :param id_of_user: идентификатор пользователя
        :return: None
        """
        connection_object.cursor.execute(f"""DELETE FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" AND id_of_user = {id_of_user}""")
        connection_object.connection.commit()

    @get_connection_and_cursor
    def update_cookie_in_session_table(self, cookie: str, id_of_user: int, name_of_cookie: str, expired: int, connection_object: ConnectionAndCursor = None):
        """
        Функция обновляет значение куки и время жизни в таблице sessions.
        :param connection_object:
        :param cookie: значение куки
        :param id_of_user: идентификатор пользователя
        :param name_of_cookie: название куки
        :param expired: время жизни
        :return: None
        """
        connection_object.cursor.execute(f"""UPDATE sessions SET cookie = "{cookie}", expired = "{expired}" WHERE id_of_user = {id_of_user} AND name_of_cookie = "{name_of_cookie}" """)
        connection_object.connection.commit()

    @get_connection_and_cursor
    def delete_pow_entry_from_pow_table(self, cookie, connection_object: ConnectionAndCursor = None):
        """
        Функция удаляет запись в таблице pow_table
        :param connection_object:
        :param cookie: значение куки
        :return:
        """
        connection_object.cursor.execute(f"""DELETE FROM pow_table WHERE cookie = "{cookie}" """)
        connection_object.connection.commit()

    @get_connection_and_cursor
    def get_pass_user_polls(self, id_of_user: int, num_of_polls: int = 4, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает список опросов, которые пользователь прошел успешно

        :param connection_object:
        :param id_of_user: идентификатор пользователя

        :param num_of_polls: количество опросов

        :return: список опросов типа Poll
        """
        connection_object.cursor.execute(f"""SELECT id_of_poll FROM table_of_users_who_pass_the_poll WHERE id_of_user = {id_of_user}""")

        response_of_query = connection_object.cursor.fetchmany(num_of_polls)
        id_of_polls = [poll[0] for poll in response_of_query]

        polls_list: list[Poll] = []

        for id_of_poll in id_of_polls:
            transaction = f"""SELECT name_of_poll, description, tags FROM polls WHERE id = {id_of_poll}"""
            connection_object.cursor.execute(transaction)
            result = connection_object.cursor.fetchall()
            for poll in result:
                polls_list.append(Poll(poll[0], poll[1], json.loads(poll[2]), id_of_poll, id_of_user, self.get_user_data_from_table(id_of_user)[0]))
        return polls_list

    @get_connection_and_cursor
    def check_user_on_pass_the_poll(self, id_of_user: int, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        """
        Проверка на то, что пользователь прошел опрос
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :param id_of_poll: идентификатор опроса
        :return: True или False
        """
        connection_object.cursor.execute(f"""SELECT * FROM table_of_users_who_pass_the_poll WHERE id_of_user = {id_of_user} AND id_of_poll = {id_of_poll}""")
        response_of_query = connection_object.cursor.fetchone()
        return True if response_of_query is not None else False

    @get_connection_and_cursor
    def delete_entry_from_users(self, id_of_user: int, connection_object: ConnectionAndCursor = None):
        """
        Функция удаляет пользователя из БД
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :return: None
        """
        connection_object.cursor.execute(f"""DELETE FROM users WHERE id_of_user={id_of_user}""")
        connection_object.connection.commit()

    @get_connection_and_cursor
    def check_availability_entry_in_sessions(self, id_of_user, connection_object: ConnectionAndCursor = None) -> bool:
        """
        Функция проверяет существование записи в таблице session со значением id_of_user
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :return: True или False
        """
        connection_object.cursor.execute(f"""SELECT id_of_user FROM sessions WHERE id_of_user = {id_of_user}""")
        if connection_object.cursor.fetchone() is None:
            return False
        return True

    def create_entry_into_sessions_table(self, cookie: str, cookie_name: str, id_of_user: int, days: int = 3):
        """
        Функция создает запись в таблице sessions
        :param cookie: значение куки
        :param cookie_name: название куки
        :param id_of_user: идентификатор пользователя
        :param days: количество дней жизни куки
        :return: None
        """
        expired = datetime.datetime.now()
        expired = expired + datetime.timedelta(days=days)
        self.create_cookie_into_session_table(cookie, cookie_name, id_of_user, expired)

    def check_user_into_superusers(self, id_of_user: int) -> bool:
        """
        Функция нужна для проверки на то, существует ли такая запись в БД со значением id_of_user
        :param id_of_user: идентификатор пользователя
        :return: True или False
        """
        if id_of_user in self.get_id_of_superusers(self):
            return True
        return False

    @get_connection_and_cursor
    def get_id_of_superusers(self, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает идентификаторы супер пользователей

        :return: список id
        """
        connection_object.cursor.execute("""SELECT id_of_superuser FROM superusers""")
        data_of_query = connection_object.cursor.fetchall()

        id_of_superusers = [idx[0] for idx in data_of_query]

        return id_of_superusers

    @get_connection_and_cursor
    def add_entry_in_ranking_table_of_users(self, id_of_user: int, vector_of_user: bytes, connection_object: ConnectionAndCursor = None):
        """
        Функция создает запись в таблице ranking_table_of_users.
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :param vector_of_user: поток байт вектора тегов пользователя
        :return: None
        """
        try:
            connection_object.cursor.execute("""INSERT INTO ranking_table_of_users (id_of_user, vector_of_user) VALUES (%s, %s)""", (id_of_user, vector_of_user))
            connection_object.connection.commit()

        except mysql.connector.errors.IntegrityError:
            connection_object.cursor.execute("""UPDATE ranking_table_of_users SET vector_of_user = %s WHERE id_of_user = %s""", (vector_of_user, id_of_user))

    @get_connection_and_cursor
    def get_vector_of_user(self, id_of_user: int, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает вектор тегов пользователя из таблицы vector_of_user
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :return: Вектор тегов пользователя
        """
        connection_object.cursor.execute(f"""SELECT vector_of_user FROM ranking_table_of_users WHERE id_of_user = {id_of_user}""")
        response_of_query = connection_object.cursor.fetchone()

        assert response_of_query is not None

        return response_of_query[0]

    @get_connection_and_cursor
    def get_tags_of_user(self, id_of_user: int, connection_object: ConnectionAndCursor = None) -> list:
        """
        Функция возвращает список тегов пользователя

        :param connection_object:
        :param id_of_user: идентификатор пользователя

        :return: список тегов
        """
        connection_object.cursor.execute(f"""SELECT tags FROM user WHERE id_of_user = {id_of_user}""")
        response_of_query = connection_object.cursor.fetchone()

        assert response_of_query is not None

        return json.loads(response_of_query[0])

    @get_connection_and_cursor
    def update_the_filed_into_user(self, id_of_user: int, field: str, value: typing.Union[str, int, datetime.date], connection_object: ConnectionAndCursor = None):
        """
        Функция является конструктором для изменения значений в таблице users
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :param field: поле для изменения
        :param value: значение на которое изменяется поле
        :return: None
        """
        transaction = f"""UPDATE user SET {field} = %s """
        transaction += f"""WHERE id_of_user = {id_of_user}"""

        connection_object.cursor.execute(transaction, (value,))
        connection_object.connection.commit()

    @get_connection_and_cursor
    def check_existence_vector_of_user_from_ranking_table(self, id_of_user: int, connection_object: ConnectionAndCursor = None) -> bool:
        """
        Функция проверяет, если ли запись в таблице ranking_table_of_users с заданным id_of_user
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :return: True или False
        """
        try:
            connection_object.cursor.execute(f"""SELECT vector_of_user FROM ranking_table_of_users WHERE id_of_user = {id_of_user}""")
            response_of_query = connection_object.cursor.fetchone()
            assert response_of_query is not None
            return True
        except AssertionError:
            return False

    @get_connection_and_cursor
    def get_count_of_users_who_pass_the_poll(self, id_of_poll: int, connection_object: ConnectionAndCursor = None) -> int:
        """
        Функция возвращает количество пользователей, которые прошли конкретный опрос

        :param connection_object:
        :param id_of_poll: идентификатор опроса
        :return: int
        """
        connection_object.cursor.execute(f"""SELECT COUNT(id_of_user) FROM table_of_users_who_pass_the_poll WHERE id_of_poll = {id_of_poll}""")
        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def get_count_of_users_who_selected_of_specific_option(self, option: str, serial_number_of_question: int, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает количество пользователей, которые выбрали конкретную опцию в вопросе
        :param connection_object:
        :param option: значение опции
        :param serial_number_of_question: порядковый номер вопроса в опросе
        :param id_of_poll: идентификатор опроса
        :return: int
        """
        connection_object.cursor.execute(f"""SELECT COUNT(id_of_user) FROM data_of_passing_poll_from_user WHERE serial_number_of_question = {serial_number_of_question} AND
        id_of_poll = {id_of_poll} AND value = "{option}" """)
        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def get_text_answers_of_users(self, id_of_poll: int, serial_number_of_questions: int, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает список текстовых ответов пользователей на вопрос
        :param connection_object:
        :param id_of_poll: идентификатор опроса
        :param serial_number_of_questions: порядковый номер вопроса в опросе
        :return: list[str]
        """
        connection_object.cursor.execute(f"""SELECT value FROM data_of_passing_poll_from_user WHERE id_of_poll = {id_of_poll} AND
        serial_number_of_question = {serial_number_of_questions}""")
        return [value[0] for value in connection_object.cursor.fetchall()]
#-----------------------------------------------------------------------------------------------------------------------
# Сохранение данных, которые пользователь ввел в ответах на опрос

    @get_connection_and_cursor
    def add_users_into_table_for_users_who_pass_the_poll(self, id_of_user, id_of_poll, connection_object: ConnectionAndCursor = None):
        """
        Функция нужна для создания записи в таблице table_of_users_who_pass_the_poll.
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :param id_of_poll: идентификатор опроса
        :return: None
        """
        try:
            connection_object.cursor.execute("""INSERT INTO table_of_users_who_pass_the_poll(id_of_user, id_of_poll) VALUES(%s, %s)""", (id_of_user, id_of_poll))
            connection_object.connection.commit()
        except mysql.connector.IntegrityError:
            raise RepeatPollError("Попытка повторного прохождения опроса")

    @get_connection_and_cursor
    def add_answer_into_table_data_of_passing_poll_from_user(self, serial_number: int, type_of_question: str, value: str, id_of_user: int, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        """
        Функция создает запись в БД с ответом пользователя на вопрос в опросе
        :param connection_object:
        :param serial_number: порядковый номер вопроса в опросе
        :param type_of_question: тип вопроса
        :param value: значение, которое выбрал или ввел пользователь
        :param id_of_user: идентификатор пользователя
        :param id_of_poll: идентификатор опроса
        :return: None
        """
        try:
            connection_object.cursor.execute("""INSERT INTO data_of_passing_poll_from_user (id, id_of_poll, id_of_user, serial_number_of_question, type_of_question, value) VALUES (%s, %s, %s, %s, %s, %s)""", (random.randint(0, 9999999), id_of_poll, id_of_user, serial_number, type_of_question, value))
            connection_object.connection.commit()
        except mysql.connector.IntegrityError:
            self.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question, value, id_of_user, id_of_poll)

    @get_connection_and_cursor
    def save_answers_users_into_table_of_passing_poll_from_user(self, answers: list, id_of_user: int, id_of_poll: int, connection_object: ConnectionAndCursor = None):
        for answer in answers:
            serial_number = answer['question_id']
            type_of_question = answer['type']
            check_the_type(type_of_question)
            value: typing.Union[str, list] = answer['value']
            if isinstance(value, list):
                for value_of_list in value:
                    client_mysqldb.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question, value_of_list, id_of_user, id_of_poll, connection_object=connection_object)
            elif isinstance(value, str):
                client_mysqldb.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question, value, id_of_user, id_of_poll, connection_object=connection_object)

        connection_object.connection.commit()

    @get_connection_and_cursor
    def delete_user_from_table_who_pass_the_poll(self, id_of_poll, id_of_user, connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(f"""DELETE FROM table_of_users_who_pass_the_poll WHERE id_of_poll = {id_of_poll}
        AND id_of_user = {id_of_user}""")
        connection_object.connection.commit()


#-----------------------------------------------------------------------------------------------------------------------


client_mysqldb = MysqlDB()