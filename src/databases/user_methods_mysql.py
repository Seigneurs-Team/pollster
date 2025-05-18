from databases.connection_shaker import get_connection_and_cursor, ConnectionAndCursor
from Configs.Exceptions import ErrorSameLogins, CookieWasExpired, NotFoundCookieIntoPowTable
from Configs.Poll import Poll
from PoW.generate_random_string import generate_random_string


import random
from mysql.connector import connect
import mysql
import datetime
import json
import typing


class UserMethodsMySQL:
    @get_connection_and_cursor
    def set_table_type_of_users(self, connection_object: ConnectionAndCursor = None):
        """
        Функция нужна для добавления в БД типов пользователей: user, staff

        :return: None
        """
        connection_object.cursor.execute("""SELECT type FROM table_of_type_of_users""")
        if connection_object.cursor.fetchone() is None:
            connection_object.cursor.execute("""INSERT INTO table_of_type_of_users(id_of_type, type) VALUES(%s, %s)""",
                                             (1, 'user'))
            connection_object.cursor.execute("""INSERT INTO table_of_type_of_users(id_of_type, type) VALUES(%s, %s)""",
                                             (2, 'staff'))
            connection_object.cursor.execute("""INSERT INTO table_of_type_of_users(id_of_type, type) VALUES(%s, %s)""",
                                             (3, 'superuser'))
            connection_object.connection.commit()

    @get_connection_and_cursor
    def create_superuser(self, connection_object: ConnectionAndCursor = None):
        """
        Функция создает суперпользователя ака админ

        :return: None
        """
        connection_object.cursor.execute("""SELECT COUNT(*) FROM superusers""")

        if connection_object.cursor.fetchone()[0] != 0:
            return None

        connection_object.cursor.execute("""INSERT INTO users (type_of_user) VALUES (%s)""", (3, ))
        connection_object.cursor.execute("""SELECT LAST_INSERT_ID()""")
        id_of_superuser = connection_object.cursor.fetchone()[0]

        connection_object.cursor.execute(
            """INSERT INTO superusers (id_of_superuser, login, password) VALUES (%s, %s, %s)""",
            (id_of_superuser, 'admin@admin-pollster.ru', 'P@ssw0rd'))

        connection_object.connection.commit()

        self.create_user('admin@admin-pollster.ru', 'P@ssw0rd', 2, 'admin', connection_object=connection_object)

    @get_connection_and_cursor
    def create_user(self, login: str, password: str, type_of_user: int, nickname: str,
                    connection_object: ConnectionAndCursor = None):
        """
        Функция создает пользователя в БД. Также есть проверка на то, что пользователь уже существует в БД с таким логином
        :param connection_object:
        :param login: логин
        :param password: пароль
        :param type_of_user: тип пользователя (user, staff)
        :param nickname: никнейм
        :return: None
        """
        connection_object.cursor.execute(f"""SELECT COUNT(*) FROM user WHERE login = "{login}" OR nickname = "{nickname}" """)
        if connection_object.cursor.fetchone()[0] != 0:
            raise ErrorSameLogins('одинаковый логин')
        connection_object.cursor.execute("""INSERT INTO users (type_of_user) VALUES (%s)""", (type_of_user, ))

        connection_object.cursor.execute("""SELECT LAST_INSERT_ID()""")
        id_of_user = connection_object.cursor.fetchone()[0]

        connection_object.cursor.execute(
            """INSERT INTO user (id_of_user, login, password, nickname) VALUES (%s, %s, %s, %s)""",
            (id_of_user, login, password, nickname))
        connection_object.connection.commit()

    @get_connection_and_cursor
    def get_user_password_and_id_of_user_from_table(self, login, connection_object: ConnectionAndCursor = None, admin: bool = False):
        """
        Функция возвращает пароль и идентификатор пользователя по логину

        :param admin:
        :param connection_object:
        :param login: логин

        :return: пароль и идентификатор пользователя
        """
        table = "user" if admin is False else "superusers"
        id_of_user_filed = "id_of_user" if admin is False else "id_of_superuser"
        connection_object.cursor.execute(f"""SELECT password, {id_of_user_filed} FROM {table} WHERE login = "{login}" """)
        response = connection_object.cursor.fetchone()
        if response is None:
            return None, None
        else:
            return response[0], response[1]

    @get_connection_and_cursor
    def get_user_nickname_from_table_with_cookie(self, cookie: str, name_of_cookie: str,
                                                 connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает никнейм пользователя по куки. Также в функции присутствует механизм проверки смерти куки.

        :param connection_object:
        :param cookie: куки значение

        :param name_of_cookie: куки название

        :return: никнейм пользователя
        """
        connection_object.cursor.execute(
            f"""SELECT expired, id_of_user FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" """)
        session = connection_object.cursor.fetchone()
        now = datetime.datetime.now()

        assert session is not None

        if now < session[0]:
            print(session)
            connection_object.cursor.execute(f"""SELECT nickname FROM user WHERE id_of_user = {session[1]}""")
            user = connection_object.cursor.fetchone()
            if user is not None:
                return user[0]
            return None

        else:
            self.delete_cookie_from_session_table(cookie, name_of_cookie, session[1])
            raise CookieWasExpired("время жизни куки файлов кончилось")

    @get_connection_and_cursor
    def get_id_of_user_from_table_with_cookies(self, cookie: str, name_of_cookie: str,
                                               connection_object: ConnectionAndCursor = None) -> str:
        """
        Функция возвращает идентификатор пользователя по куки из таблицы sessions
        :param connection_object:
        :param cookie: куки значение
        :param name_of_cookie: имя куки
        :return: идентификатор пользователя
        """
        connection_object.cursor.execute(
            f"""SELECT id_of_user FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" """)
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
        connection_object.cursor.execute(
            f"""SELECT nickname, login, number_of_phone, date_of_birth, tags FROM user WHERE id_of_user={id_of_user}""")
        response_of_query = connection_object.cursor.fetchone()
        return response_of_query if response_of_query is not None else ["Deleted User"]

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
    def create_cookie_into_session_table(self, cookie: str, name_of_cookie: str, id_of_user: int,
                                         expired: datetime.datetime, connection_object: ConnectionAndCursor = None):
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
            connection_object.cursor.execute(
                f"""SELECT id_of_cookie FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" """)
            if connection_object.cursor.fetchone() is not None:
                raise Exception

            connection_object.cursor.execute(
                f"""INSERT INTO sessions (id_of_user, cookie, name_of_cookie, expired, id_of_cookie) VALUES (%s, %s, %s, %s, %s)""",
                (id_of_user, cookie, name_of_cookie, expired, random.randint(0, 10 ** 4)))
            connection_object.connection.commit()

        except mysql.connector.IntegrityError:
            self.create_cookie_into_session_table(cookie, name_of_cookie, id_of_user, expired)
        except Exception:
            new_cookie = generate_random_string(10)
            self.create_cookie_into_session_table(new_cookie, name_of_cookie, id_of_user, expired)

    @get_connection_and_cursor
    def delete_cookie_from_session_table(self, cookie: str, name_of_cookie: str, id_of_user: int,
                                         connection_object: ConnectionAndCursor = None):
        """
        Удаление записи в sessions
        :param connection_object:
        :param cookie: значение куки
        :param name_of_cookie: название куки
        :param id_of_user: идентификатор пользователя
        :return: None
        """
        connection_object.cursor.execute(
            f"""DELETE FROM sessions WHERE cookie = "{cookie}" AND name_of_cookie = "{name_of_cookie}" AND id_of_user = {id_of_user}""")
        connection_object.connection.commit()

    @get_connection_and_cursor
    def update_cookie_in_session_table(self, cookie: str, id_of_user: int, name_of_cookie: str, expired: int,
                                       connection_object: ConnectionAndCursor = None):
        """
        Функция обновляет значение куки и время жизни в таблице sessions.
        :param connection_object:
        :param cookie: значение куки
        :param id_of_user: идентификатор пользователя
        :param name_of_cookie: название куки
        :param expired: время жизни
        :return: None
        """
        connection_object.cursor.execute(
            f"""UPDATE sessions SET cookie = "{cookie}", expired = "{expired}" WHERE id_of_user = {id_of_user} AND name_of_cookie = "{name_of_cookie}" """)
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
    def get_pass_user_polls(self, id_of_user: int, num_of_polls: int = 4,
                            connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает список опросов, которые пользователь прошел успешно

        :param connection_object:
        :param id_of_user: идентификатор пользователя

        :param num_of_polls: количество опросов

        :return: список опросов типа Poll
        """
        connection_object.cursor.execute(
            f"""SELECT id_of_poll FROM table_of_users_who_pass_the_poll WHERE id_of_user = {id_of_user}""")

        response_of_query = connection_object.cursor.fetchmany(num_of_polls)
        id_of_polls = [poll[0] for poll in response_of_query]

        polls_list: list[Poll] = []

        for id_of_poll in id_of_polls:
            transaction = f"""SELECT name_of_poll, description, tags FROM polls WHERE id = {id_of_poll}"""
            connection_object.cursor.execute(transaction)
            result = connection_object.cursor.fetchall()
            for poll in result:
                polls_list.append(
                    Poll(
                        poll[0], poll[1], json.loads(poll[2]),
                        id_of_poll, id_of_user, self.get_user_data_from_table(id_of_user)[0],
                        self.get_cover_of_poll_in_base64_format(id_of_poll, connection_object=connection_object)
                    )
                )
        return polls_list

    @get_connection_and_cursor
    def check_user_on_pass_the_poll(self, id_of_user: int, id_of_poll: int,
                                    connection_object: ConnectionAndCursor = None):
        """
        Проверка на то, что пользователь прошел опрос
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :param id_of_poll: идентификатор опроса
        :return: True или False
        """
        connection_object.cursor.execute(
            f"""SELECT * FROM table_of_users_who_pass_the_poll WHERE id_of_user = {id_of_user} AND id_of_poll = {id_of_poll}""")
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
        if id_of_user in self.get_id_of_superusers():
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
    def add_entry_in_ranking_table_of_users(self, id_of_user: int, vector_of_user: bytes,
                                            connection_object: ConnectionAndCursor = None):
        """
        Функция создает запись в таблице ranking_table_of_users.
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :param vector_of_user: поток байт вектора тегов пользователя
        :return: None
        """
        try:
            connection_object.cursor.execute(
                """INSERT INTO ranking_table_of_users (id_of_user, vector_of_user) VALUES (%s, %s)""",
                (id_of_user, vector_of_user))
            connection_object.connection.commit()

        except mysql.connector.errors.IntegrityError:
            connection_object.cursor.execute(
                """UPDATE ranking_table_of_users SET vector_of_user = %s WHERE id_of_user = %s""",
                (vector_of_user, id_of_user))

    @get_connection_and_cursor
    def get_vector_of_user(self, id_of_user: int, connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает вектор тегов пользователя из таблицы vector_of_user
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :return: Вектор тегов пользователя
        """
        connection_object.cursor.execute(
            f"""SELECT vector_of_user FROM ranking_table_of_users WHERE id_of_user = {id_of_user}""")
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
    def update_the_filed_into_user(self, id_of_user: int, field: str, value: typing.Union[str, int, datetime.date],
                                   connection_object: ConnectionAndCursor = None):
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
    def check_existence_vector_of_user_from_ranking_table(self, id_of_user: int,
                                                          connection_object: ConnectionAndCursor = None) -> bool:
        """
        Функция проверяет, если ли запись в таблице ranking_table_of_users с заданным id_of_user
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :return: True или False
        """
        try:
            connection_object.cursor.execute(
                f"""SELECT vector_of_user FROM ranking_table_of_users WHERE id_of_user = {id_of_user}""")
            response_of_query = connection_object.cursor.fetchone()
            assert response_of_query is not None
            return True
        except AssertionError:
            return False

    @get_connection_and_cursor
    def get_count_of_users_who_pass_the_poll(self, id_of_poll: int,
                                             connection_object: ConnectionAndCursor = None) -> int:
        """
        Функция возвращает количество пользователей, которые прошли конкретный опрос

        :param connection_object:
        :param id_of_poll: идентификатор опроса
        :return: int
        """
        connection_object.cursor.execute(
            f"""SELECT COUNT(id_of_user) FROM table_of_users_who_pass_the_poll WHERE id_of_poll = {id_of_poll}""")
        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def get_count_of_users_who_selected_of_specific_option(self, option: str, serial_number_of_question: int,
                                                           id_of_poll: int,
                                                           connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает количество пользователей, которые выбрали конкретную опцию в вопросе
        :param connection_object:
        :param option: значение опции
        :param serial_number_of_question: порядковый номер вопроса в опросе
        :param id_of_poll: идентификатор опроса
        :return: int
        """
        connection_object.cursor.execute(
            f"""SELECT COUNT(id_of_user) FROM data_of_passing_poll_from_user WHERE serial_number_of_question = {serial_number_of_question} AND
            id_of_poll = {id_of_poll} AND value = "{option}" """)
        return connection_object.cursor.fetchone()[0]

    @get_connection_and_cursor
    def get_text_answers_of_users(self, id_of_poll: int, serial_number_of_questions: int,
                                  connection_object: ConnectionAndCursor = None):
        """
        Функция возвращает список текстовых ответов пользователей на вопрос
        :param connection_object:
        :param id_of_poll: идентификатор опроса
        :param serial_number_of_questions: порядковый номер вопроса в опросе
        :return: list[str]
        """
        connection_object.cursor.execute(
            f"""SELECT value FROM data_of_passing_poll_from_user WHERE id_of_poll = {id_of_poll} AND
            serial_number_of_question = {serial_number_of_questions}""")
        return [value[0] for value in connection_object.cursor.fetchall()]