import datetime
import random

from mysql.connector import connect
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

from Configs.Exceptions import NotFoundPoll, ErrorSameLogins, NotFoundCookieIntoPowTable, CookieWasExpired, RepeatPollError
from PoW.generate_random_string import generate_random_string
logger = logging.getLogger()


class MysqlDB:
    def __init__(self):
        self.connection, self.cursor = self.connect_to_db()
        self.create_table()

    def connect_to_db(self):
        try:
            connection = connect(
                host=Hosts.mysql_db,
                user='root',
                password='root1234567890',
                auth_plugin='mysql_native_password',
                database='Pollster_DB'
            )
            logger.info('Успешное подключение')
            return connection, connection.cursor(buffered=True)
        except (mysql.connector.errors.ProgrammingError, mysql.connector.errors.DatabaseError):
            connection = connect(
                host=Hosts.mysql_db,
                user='root',
                password='root1234567890',
                auth_plugin='mysql_native_password',
            )
            cursor = connection.cursor()
            cursor.execute('CREATE DATABASE Pollster_DB')
            connection.commit()
            self.connect_to_db()

    def create_table(self):
        #polls
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS polls(id INT UNSIGNED, tags TEXT, name_of_poll TEXT, description TEXT, id_of_author INT, PRIMARY KEY (id))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS questions(id_of_question INT UNSIGNED, id_of_poll INT UNSIGNED, text_of_question TEXT, type_of_question TEXT, serial_number INT, FOREIGN KEY (id_of_question) REFERENCES polls (id) ON DELETE CASCADE)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS options(id_of_option INT UNSIGNED, id_of_question INT UNSIGNED, option_name TEXT, FOREIGN KEY (id_of_option) REFERENCES questions (id_of_question) ON DELETE CASCADE)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS rightAnswers(id_of_question INT UNSIGNED, rightAnswerId INT UNSIGNED, FOREIGN KEY (id_of_question) REFERENCES questions (id_of_question) ON DELETE CASCADE)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS text_rights_answers(id_of_question INT UNSIGNED, text_of_right_answer TEXT, FOREIGN KEY (id_of_question) REFERENCES questions (id_of_question) ON DELETE CASCADE)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS types_of_question(id INT, type TEXT, PRIMARY KEY (id))""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ranking_table(id_of_poll INT, vector_of_poll BLOB, FOREIGN KEY(id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")

        #users
        #id_of_user состоит из последовательности длинной 6 цифр со знаком минус
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(id_of_user INT, password TEXT, login TEXT, type_of_user TEXT, login_in_account BOOL, nickname TEXT, PRIMARY KEY (id_of_user))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS sessions(id_of_user INT, id_of_cookie INT, cookie TEXT, expired TIMESTAMP, name_of_cookie TEXT, PRIMARY KEY (id_of_cookie))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS pow_table(pow INT, cookie TEXT)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS table_of_type_of_users(id_of_type INT, type TEXT, PRIMARY KEY (id_of_type))""")

        #superuser
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS superusers(id_of_superuser INT, login TEXT, password TEXT, PRIMARY KEY (id_of_superuser))""")
        #данные, которые пользователь ввел в ответах на опрос
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS table_of_users_who_pass_the_poll(id_of_user INT, id_of_poll INT)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS data_of_passing_poll_from_user(id INT, id_of_poll INT, id_of_user INT, serial_number_of_question INT, type_of_question TEXT, value TEXT, PRIMARY KEY (id))""")

        self.connection.commit()
        self.set_types_of_questions()

#-----------------------------------------------------------------------------------------------------------------------
# часть кода связанная с созданием, редактированием и удалением опросов

    def get_polls_tags(self, id_of_poll: int):
        self.cursor.execute(f"""SELECT tags FROM polls WHERE id={id_of_poll}""")
        response_of_query = self.cursor.fetchone()

        assert response_of_query is not None

        return response_of_query[0]

    def get_polls(self, num_of_polls: int = 4, id_of_user: int = None) -> list:
        """
        Функция возвращает list, состоящий из id: int, tags: string, name_of_poll: string, description: string
        :param num_of_polls: количество опросов, которые должна вернуть функция
        :param id_of_user: уникальный идентификатор пользователя
        :return: list
        """
        transaction = """SELECT name_of_poll, description, tags, id FROM polls"""
        if id_of_user is not None:
            transaction += f" WHERE id_of_author = {id_of_user}" if id_of_user is not None else ''
        self.cursor.execute(transaction)
        result = self.cursor.fetchmany(num_of_polls)
        polls_list: list[Poll] = []
        for poll in result:
            polls_list.append(Poll(poll[0], poll[1], poll[2], poll[3], id_of_user))
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
        dict_of_poll: dict = {
            'id_of_poll': id_of_poll,
            'name_of_poll': questions_entries[0][1],
            'description': questions_entries[0][3],
            'tags': questions_entries[0][2],
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

            elif type_of_question == 'radiobutton' or type_of_question == 'checkbox':
                dict_of_poll['questions'][index]['options'] = self.get_options(id_of_question)
                dict_of_poll['questions'][index]['rightAnswersId'] = self.get_right_answers(id_of_question)
        return dict_of_poll

    def get_questions(self, id_of_poll: int) -> List or None:
        self.cursor.execute(f"""SELECT polls.id, polls.name_of_poll, polls.tags, 
                 polls.description, questions.id_of_question, questions.type_of_question, questions.text_of_question,
                 questions.serial_number
                 FROM polls INNER JOIN questions ON polls.id = questions.id_of_poll
                 WHERE polls.id = {id_of_poll}""")
        response_from_query = self.cursor.fetchall()
        print(response_from_query)

        if len(response_from_query) == 0:
            raise NotFoundPoll('Опрос не найден')
        return response_from_query

    def get_options(self, id_of_question: int) -> list[str]:
        """
        Функция выполняет выборку записей из таблицы options по ключевому ключу id_of_question
        :param id_of_question: идентификатор вопроса
        :return: возвращает список объекта Option
        """
        self.cursor.execute(f"""SELECT option_name FROM options WHERE id_of_question = {id_of_question}""")
        response_from_query = self.cursor.fetchall()

        return [option[0] for option in response_from_query]

    def get_text_right_answers(self, id_of_question: int) -> str:
        """
        Функция выполняет выборку записей из таблицы text_rights_answers по ключевому ключу id_of_question
        :param id_of_question: идентификатор вопроса
        :return: возвращает список объекта RightTextAnswer
        """
        self.cursor.execute(f"""SELECT text_of_right_answer FROM text_rights_answers WHERE id_of_question = {id_of_question}""")
        response_of_query = self.cursor.fetchall()

        return response_of_query[0][0]

    def get_right_answers(self, id_of_question: int):
        """
        Функция выполняет выборку записей из таблицы rightAnswers по ключевому ключу id_of_question
        :return:
        """

        self.cursor.execute(f"""SELECT rightAnswerId FROM rightAnswers WHERE id_of_question={id_of_question}""")
        response_of_query = self.cursor.fetchall()

        return [right_answer_id[0] for right_answer_id in response_of_query]

    def create_pool(
            self,
            poll: Poll,
            list_of_questions: list[Question],
            list_of_options: list[Option],
            list_of_right_answers: list[RightAnswer],
            list_of_text_right_answers: list[RightTextAnswer]
    ) -> bool:
        """
        Функция создает опрос в базе данных
        :param poll: объект класса Poll
        :param list_of_questions: объект класса list[Question]
        :param list_of_options: объект класса list[Option]
        :param list_of_right_answers: объект класса list[RightAnswer]
        :param list_of_text_right_answers: объект класса list[RightTextAnswer]
        :return: возвращает 1 или 0; 1 означает success create poll, 0 означает, что транзакция не была совершена
        """
        try:
            self.add_new_entry_into_polls_table(poll)
            for question in list_of_questions:
                self.add_new_entry_into_questions_table(question)

            for option in list_of_options:
                self.add_new_entry_into_options_table(option)

            for right_answer in list_of_right_answers:
                self.add_new_entry_into_right_answers_table(right_answer)
            for right_text_answer in list_of_text_right_answers:
                self.add_new_entry_into_text_rights_answers_table(right_text_answer)
            self.connection.commit()
            return True
        except Exception as ex:
            logger.warning('Транзакция не была успешно выполнена. Опрос не был создан', exc_info=ex)
            return False

    def add_new_entry_into_polls_table(self, poll: Poll) -> None:
        """
        Добавляет запись в таблицу polls
        :param poll: объект класса Poll
        :return:
        """
        try:
            self.cursor.execute("""INSERT INTO polls(id, tags, name_of_poll, description, id_of_author) VALUES (%s, %s, %s, %s, %s)""",
                                (poll.id_of_poll, poll.tags, poll.name_of_poll, poll.description, poll.id_of_author))
        except mysql.connector.errors.IntegrityError:
            poll.id_of_poll = get_random_id()
            self.add_new_entry_into_polls_table(poll)

    def add_new_entry_into_questions_table(self, question: Question) -> None:
        """
        Добавляет запись в таблицу questions
        :param question: объект класса Question
        :return:
        """
        try:
            self.cursor.execute("""INSERT INTO questions(id_of_question, id_of_poll, text_of_question, type_of_question, serial_number) VALUES (%s, %s, %s, %s, %s)""",
                                (question.id_of_question, question.id_of_poll, question.text_of_question, question.type_of_question, question.serial_number))
        except mysql.connector.errors.IntegrityError:
            question.id_of_question = get_random_id()
            self.add_new_entry_into_questions_table(question)

    def add_new_entry_into_options_table(self, option: Option) -> None:
        """
        Добавляет запись в таблицу options
        :param option: объект класса Option
        :return:
        """
        try:
            self.cursor.execute("""INSERT INTO options(id_of_option, id_of_question, option_name) VALUES (%s, %s, %s)""",
                                (option.id_of_option, option.id_of_question, option.option))
        except mysql.connector.errors.IntegrityError:
            option.id_of_option = get_random_id()
            self.add_new_entry_into_options_table(option)

    def add_new_entry_into_right_answers_table(self, right_answer: RightAnswer) -> None:
        """
        Добавляет запись в таблицу rightAnswers
        :param right_answer: объект класса RightAnswer
        :return:
        """
        self.cursor.execute("""INSERT INTO rightAnswers(id_of_question, rightAnswerId) VALUES (%s, %s)""",
                            (right_answer.id_of_question, right_answer.RightAnswerId))

    def add_new_entry_into_text_rights_answers_table(self, right_text_answer: RightTextAnswer) -> None:
        """
        Добавляет запись в таблицу text_rights_answers
        :param right_text_answer: объект класса RightTextAnswer
        :return:
        """
        self.cursor.execute("""INSERT INTO text_rights_answers(id_of_question, text_of_right_answer) VALUES(%s, %s)""",
                            (right_text_answer.id_of_question, right_text_answer.text_of_right_answer))

    def set_types_of_questions(self):
        self.cursor.execute("""SELECT id FROM types_of_question""")
        types_of_question = ['long text', 'short text', 'radiobutton', 'checkbox']
        if self.cursor.fetchone() is None:
            for i, type_of_question in enumerate(types_of_question):
                self.cursor.execute("""INSERT INTO types_of_question(id, type) VALUES (%s, %s)""", (i, type_of_question))
            self.connection.commit()
        else:
            return None

    def get_types_of_question(self):
        self.cursor.execute("""SELECT type FROM types_of_question""")
        result = self.cursor.fetchall()
        return [type_of_question[0] for type_of_question in result]

    def get_id_of_author_of_poll(self, id_of_poll):
        self.cursor.execute(f"""SELECT id_of_author FROM polls WHERE id={id_of_poll}""")
        data_of_query = self.cursor.fetchone()
        if data_of_query is None:
            raise NotFoundPoll('Не найден опрос с данным id')

        return data_of_query[0]

    def delete_poll(self, id_of_poll: int):
        self.cursor.execute(f"""DELETE FROM polls, questions, options,  WHERE id={id_of_poll}""")
        self.connection.commit()

    def create_entry_into_ranking_table(self, id_of_poll: int, vector_of_poll: bytes):
        self.cursor.execute("""INSERT INTO ranking_table(id_of_poll, vector_of_poll) VALUES(%s, %s)""", (id_of_poll, vector_of_poll))
        self.connection.commit()

    def get_vectorization_polls(self, id_of_user: int):
        self.cursor.execute(f"""SELECT ranking_table.id_of_poll, ranking_table.vector_of_poll 
        FROM ranking_table INNER JOIN table_of_users_who_pass_the_poll 
        ON table_of_users_who_pass_the_poll.id_of_user != {id_of_user}""")

        response_of_query = self.cursor.fetchall()

        return response_of_query

#-----------------------------------------------------------------------------------------------------------------------
# часть кода связанная с методами базы данных: подключение, переподключение, удаление таблиц

    def reconnect(self):
        self.connection, self.cursor = self.connect_to_db()

    def delete_tables(self):
        self.cursor.execute("""DROP TABLE polls, questions, options, rightAnswers""")
        self.connection.commit()
#-----------------------------------------------------------------------------------------------------------------------
# часть кода связанная с методами пользователей

    def create_superuser(self):
        try:
            self.cursor.execute("""INSERT INTO superusers (id_of_superusers, login, password) VALUES (%s, %s, %s)""", (random.randint(-99999999, -9999999), 'admin', 'P@ssw0rd'))
        except mysql.connector.IntegrityError:
            self.create_superuser()
        self.connection.commit()

    def create_user(self, login: str, password: str, type_of_user: str, nickname: str):
        self.cursor.execute(f"""SELECT * FROM users WHERE login = "{login}" """)
        if len(self.cursor.fetchall()) != 0:
            raise ErrorSameLogins('одинаковый логин')
        try:
            id_of_user = random.randint(-9999999, -999999)
            self.cursor.execute("""INSERT INTO users (id_of_user, login, password, type_of_user, login_in_account, nickname) VALUES (%s, %s, %s, %s, %s, %s)""", (id_of_user, login, password, type_of_user, True, nickname))
        except mysql.connector.IntegrityError:
            self.create_user(login, password, type_of_user, nickname)

        self.connection.commit()

    def get_user_password_and_id_of_user_from_table(self, login):
        self.cursor.execute(f"""SELECT password, id_of_user FROM users WHERE login = "{login}" """)
        response = self.cursor.fetchone()
        if response is None:
            return None, None
        else:
            return response[0], response[1]

    def get_user_nickname_from_table_with_cookie(self, cookie: str, name_of_cookie: str):
        self.cursor.execute(f"""SELECT expired, id_of_user FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" """)
        session = self.cursor.fetchone()
        now = datetime.datetime.now()

        assert session is not None

        if now < session[0]:
            self.cursor.execute(f"""SELECT nickname FROM users WHERE id_of_user = {session[1]}""")
            user = self.cursor.fetchone()
            if user is not None:
                return user[0]
            return None

        else:
            self.delete_cookie_from_session_table(cookie, name_of_cookie, session[1])
            raise CookieWasExpired("время жизни куки файлов кончилось")

    def get_id_of_user_from_table_with_cookies(self, cookie: str, name_of_cookie: str) -> str:
        self.cursor.execute(f"""SELECT id_of_user FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" """)
        session = self.cursor.fetchone()
        return session[0]

    def get_user_data_from_table(self, id_of_user: int) -> tuple:
        self.cursor.execute(f"""SELECT nickname, login FROM users WHERE id_of_user={id_of_user}""")
        return self.cursor.fetchone()

    def create_cookie_into_pow_table(self, cookie: str):
        try:
            self.cursor.execute("""INSERT INTO pow_table (cookie) VALUES (%s)""", (cookie, ))
        except mysql.connector.IntegrityError:
            raise Exception
        self.connection.commit()

    def update_pow_in_pow_table(self, cookie: str, pow: int):
        self.cursor.execute(f"""UPDATE pow_table SET pow = {pow} WHERE cookie = "{cookie}" """)
        self.connection.commit()

    def get_pow(self, cookie: str):
        self.cursor.execute(f"""SELECT pow FROM pow_table WHERE cookie = "{cookie}" """)
        response = self.cursor.fetchall()
        if len(response) != 0:
            return response[0][0]
        else:
            raise NotFoundCookieIntoPowTable('не найден куки в таблице')

    def create_cookie_into_session_table(self, cookie: str, name_of_cookie: str, id_of_user: int, expired: datetime.datetime):
        try:
            self.cursor.execute(f"""SELECT id_of_cookie FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" """)
            if self.cursor.fetchone() is not None:
                raise Exception

            self.cursor.execute(f"""INSERT INTO sessions (id_of_user, cookie, name_of_cookie, expired, id_of_cookie) VALUES (%s, %s, %s, %s, %s)""", (id_of_user, cookie, name_of_cookie, expired, random.randint(0, 10**4)))
            self.connection.commit()
        except mysql.connector.IntegrityError:
            self.create_cookie_into_session_table(cookie, name_of_cookie, id_of_user, expired)
        except Exception:
            new_cookie = generate_random_string(10)
            self.create_cookie_into_session_table(new_cookie, name_of_cookie, id_of_user, expired)

    def delete_cookie_from_session_table(self, cookie: str, name_of_cookie: str, id_of_user: int):
        self.cursor.execute(f"""DELETE FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" AND id_of_user = {id_of_user}""")
        self.connection.commit()

    def update_cookie_in_session_table(self, cookie: str, id_of_user: int, name_of_cookie: str, expired: int):
        self.cursor.execute(f"""UPDATE sessions SET cookie = "{cookie}", expired = "{expired}" WHERE id_of_user = {id_of_user} AND name_of_cookie = "{name_of_cookie}" """)
        self.connection.commit()

    def delete_pow_entry_from_pow_table(self, cookie):
        self.cursor.execute(f"""DELETE FROM pow_table WHERE cookie = "{cookie}" """)
        self.connection.commit()

    def get_pass_user_polls(self, id_of_user: int, num_of_polls: int = 4):
        self.cursor.execute(f"""SELECT id_of_poll FROM table_of_users_who_pass_the_poll WHERE id_of_user = {id_of_user}""")
        id_of_polls = [poll[0] for poll in self.cursor.fetchmany(num_of_polls)]

        polls_list: list[Poll] = []

        for id_of_poll in id_of_polls:
            transaction = f"""SELECT name_of_poll, description, tags FROM polls WHERE id = {id_of_poll}"""
            self.cursor.execute(transaction)
            result = self.cursor.fetchall()
            for poll in result:
                polls_list.append(Poll(poll[0], poll[1], poll[2], poll[3], id_of_user))
        return polls_list

    def delete_entry_from_users(self, id_of_user: int):
        self.cursor.execute(f"""DELETE FROM users WHERE id_of_user={id_of_user}""")
        self.connection.commit()

    def check_availability_entry_in_sessions(self, id_of_user) -> bool:
        self.cursor.execute(f"""SELECT id_of_user FROM sessions WHERE id_of_user = {id_of_user}""")
        if self.cursor.fetchone() is None:
            return False
        return True

    def create_entry_into_sessions_table(self, cookie: str, cookie_name: str, id_of_user: int,  days: int = 3):
        expired = datetime.datetime.now()
        expired = expired + datetime.timedelta(days=days)
        self.create_cookie_into_session_table(cookie, cookie_name, id_of_user, expired)

    def check_user_into_superusers(self, id_of_user: int) -> bool:
        if id_of_user in self.get_id_of_superusers():
            return True
        return False

    def get_id_of_superusers(self):
        self.cursor.execute("""SELECT id_of_superuser FROM superusers""")
        data_of_query = self.cursor.fetchall()

        id_of_superusers = [idx[0] for idx in data_of_query]

        return id_of_superusers

#-----------------------------------------------------------------------------------------------------------------------
# Сохранение данных, которые пользователь ввел в ответах на опрос

    def add_users_into_table_for_users_who_pass_the_poll(self, id_of_user, id_of_poll):
        try:
            self.cursor.execute("""INSERT INTO table_of_users_who_pass_the_poll(id_of_user, id_of_poll) VALUES(%s, %s)""", (id_of_user, id_of_poll))
            self.connection.commit()
        except mysql.connector.IntegrityError:
            raise RepeatPollError("Попытка повторного прохождения опроса")

    def add_answer_into_table_data_of_passing_poll_from_user(self, serial_number: int, type_of_question: str, value: str, id_of_user: int, id_of_poll: int):
        try:
            self.cursor.execute("""INSERT INTO data_of_passing_poll_from_user (id, id_of_poll, id_of_user, serial_number_of_question, type_of_question, value) VALUES (%s, %s, %s, %s, %s, %s)""", (random.randint(0, 9999999), id_of_poll, id_of_user, serial_number, type_of_question, value))
            self.connection.commit()
        except mysql.connector.IntegrityError:
            self.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question, value, id_of_user, id_of_poll)
#-----------------------------------------------------------------------------------------------------------------------


client_mysqldb = MysqlDB()