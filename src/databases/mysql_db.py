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
from app.create_poll_page.set_poll import get_random_id
from typing import List

from Configs.Exceptions import NotFoundPoll
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
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS polls(id INT UNSIGNED, tags TEXT, name_of_poll TEXT, description TEXT, PRIMARY KEY (id))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS questions(id_of_question INT UNSIGNED, id_of_poll INT UNSIGNED, text_of_question TEXT, type_of_question TEXT, PRIMARY KEY(id_of_question))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS options(id_of_option INT UNSIGNED, id_of_question INT UNSIGNED, option_name TEXT, PRIMARY KEY(id_of_option))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS rightAnswers(id_of_question INT UNSIGNED, rightAnswerId INT UNSIGNED)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS text_rights_answers(id_of_question INT UNSIGNED, text_of_right_answer TEXT, PRIMARY KEY (id_of_question))""")
        self.connection.commit()

    def get_polls(self, num_of_polls: int = 4) -> list:
        """
        Функция возвращает list, состоящий из id: int, tags: string, name_of_poll: string, description: string
        :param num_of_polls: количество опросов, которые должна вернуть функция
        :return: list
        """
        self.cursor.execute("""SELECT * FROM polls""")
        result = self.cursor.fetchmany(num_of_polls)
        polls_list: list[Poll] = []
        for poll in result:
            polls_list.append(Poll(poll[3], poll[2], poll[1], poll[0]))
        return polls_list

    def get_poll(self, id_of_poll: int) -> dict or None:
        """
        Функция выполняет транзакцию, у которой ответ состоит из перекрытия полей четырех таблиц.

        :param id_of_poll: идентификатор опроса
        :return: None
        """
        # self.cursor.execute(f"""SELECT polls.name_of_poll, polls.description, polls.tags, polls.description,
        #  questions.text_of_question, questions.type_of_question, options.option_name, rightAnswers.rightAnswerId
        #  FROM polls INNER JOIN questions ON polls.id = questions.id_of_poll
        #  INNER JOIN options ON questions.id_of_question = options.id_of_question
        #  INNER JOIN rightAnswers ON options.id_of_option = rightAnswers.id_of_option
        #  WHERE polls.id = {id_of_poll}""")

        # self.cursor.execute(f"""SELECT polls.id, questions.id_of_question
        #          FROM polls INNER JOIN questions ON polls.id = questions.id_of_poll
        #          WHERE polls.id = {id_of_poll}""")

        questions_entries = self.get_questions(id_of_poll)
        dict_of_poll = self.set_dict_poll(questions_entries, id_of_poll)
        return dict_of_poll

    def set_dict_poll(self, questions_entries: list, id_of_poll: int) -> dict:
        print(questions_entries)
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

            dict_of_poll['questions'].append({
                'id': id_of_question,
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
                 polls.description, questions.id_of_question, questions.type_of_question, questions.text_of_question
                 FROM polls INNER JOIN questions ON polls.id = questions.id_of_poll
                 WHERE polls.id = {id_of_poll}""")
        response_from_query = self.cursor.fetchall()

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
            self.cursor.execute("""INSERT INTO polls(id, tags, name_of_poll, description) VALUES (%s, %s, %s, %s)""",
                                (poll.id_of_poll, poll.tags, poll.name_of_poll, poll.description))
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
            self.cursor.execute("""INSERT INTO questions(id_of_question, id_of_poll, text_of_question, type_of_question) VALUES (%s, %s, %s, %s)""",
                                (question.id_of_question, question.id_of_poll, question.text_of_question, question.type_of_question))
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

    def reconnect(self):
        self.connection, self.cursor = self.connect_to_db()

    def delete_tables(self):
        self.cursor.execute("""DROP TABLE polls, questions, options, rightAnswers""")
        self.connection.commit()


client_mysqldb = MysqlDB()