from databases.connection_shaker import get_connection_and_cursor, ConnectionAndCursor
from Configs.Exceptions import RepeatPollError

import mysql.connector
import random
import typing


class PassPollsMethods:
    @get_connection_and_cursor
    def add_users_into_table_for_users_who_pass_the_poll(self, id_of_user, id_of_poll,
                                                         connection_object: ConnectionAndCursor = None):
        """
        Функция нужна для создания записи в таблице table_of_users_who_pass_the_poll.
        :param connection_object:
        :param id_of_user: идентификатор пользователя
        :param id_of_poll: идентификатор опроса
        :return: None
        """
        try:
            connection_object.cursor.execute(
                """INSERT INTO table_of_users_who_pass_the_poll(id_of_user, id_of_poll) VALUES(%s, %s)""",
                (id_of_user, id_of_poll))
            connection_object.connection.commit()
        except mysql.connector.IntegrityError:
            raise RepeatPollError("Попытка повторного прохождения опроса")

    @get_connection_and_cursor
    def add_answer_into_table_data_of_passing_poll_from_user(self, serial_number: int, type_of_question: str,
                                                             value: str, id_of_user: int, id_of_poll: int,
                                                             connection_object: ConnectionAndCursor = None):
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
            connection_object.cursor.execute(
                """INSERT INTO data_of_passing_poll_from_user (id, id_of_poll, id_of_user, serial_number_of_question, type_of_question, value) VALUES (%s, %s, %s, %s, %s, %s)""",
                (random.randint(0, 9999999), id_of_poll, id_of_user, serial_number, type_of_question, value))
            connection_object.connection.commit()
        except mysql.connector.IntegrityError:
            self.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question, value,
                                                                      id_of_user, id_of_poll)

    @get_connection_and_cursor
    def save_answers_users_into_table_of_passing_poll_from_user(self, answers: list, id_of_user: int, id_of_poll: int,
                                                                connection_object: ConnectionAndCursor = None):
        for answer in answers:
            serial_number = answer['question_id']
            type_of_question = answer['type']
            # check_the_type(type_of_question)
            value: typing.Union[str, list] = answer['value']
            if isinstance(value, list):
                for value_of_list in value:
                    self.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question,
                                                                              value_of_list, id_of_user,
                                                                              id_of_poll,
                                                                              connection_object=connection_object)
            elif isinstance(value, str):
                self.add_answer_into_table_data_of_passing_poll_from_user(serial_number, type_of_question,
                                                                          value, id_of_user, id_of_poll,
                                                                          connection_object=connection_object)

        connection_object.connection.commit()

    @get_connection_and_cursor
    def delete_user_from_table_who_pass_the_poll(self, id_of_poll, id_of_user,
                                                 connection_object: ConnectionAndCursor = None):
        connection_object.cursor.execute(
            f"""DELETE FROM table_of_users_who_pass_the_poll WHERE id_of_poll = {id_of_poll}
            AND id_of_user = {id_of_user}""")
        connection_object.connection.commit()