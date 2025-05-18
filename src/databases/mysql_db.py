from Configs.Exceptions import TryToXSS

from databases.connection_shaker import get_connection_and_cursor, ConnectionAndCursor
from databases.user_methods_mysql import UserMethodsMySQL
from databases.polls_methods_mysql import PollsMethodsMySQL
from databases.pass_polls_methods import PassPollsMethods

from Configs.Hosts import Hosts

from mysql.connector import connect, pooling
import mysql.connector

from logging import getLogger

logger = getLogger()


def check_the_type(type_of_question: str):
    """
    Проверка значений поля type на несоответствие со значениями из БД.
    :param type_of_question: тип вопроса
    :return: None
    """
    types = client_mysqldb.get_types_of_question()
    if type_of_question not in types:
        raise TryToXSS("попытка XSS атаки")


class MysqlDB(UserMethodsMySQL, PollsMethodsMySQL, PassPollsMethods):
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
        # polls
        connection_object.cursor.execute(
            """CREATE TABLE IF NOT EXISTS polls(id INT AUTO_INCREMENT, tags VARCHAR(100), name_of_poll VARCHAR(100), description TEXT, id_of_author INT, PRIMARY KEY (id))""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS questions(id_of_question INT AUTO_INCREMENT, 
        id_of_poll INT, text_of_question VARCHAR(100), type_of_question VARCHAR(50), serial_number INT,
        PRIMARY KEY (id_of_question),
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS options(id_of_option INT AUTO_INCREMENT PRIMARY KEY, id_of_question INT, 
        option_name VARCHAR(100),
        FOREIGN KEY (id_of_question) REFERENCES questions (id_of_question) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS rightAnswers(id_of_question INT, rightAnswerId INT, 
        PRIMARY KEY (id_of_question, rightAnswerId), FOREIGN KEY (id_of_question) REFERENCES questions (id_of_question) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS text_rights_answers(id_of_question INT, text_of_right_answer TEXT, 
        PRIMARY KEY (id_of_question), FOREIGN KEY (id_of_question) REFERENCES questions (id_of_question) ON DELETE CASCADE)""")

        connection_object.cursor.execute(
            """CREATE TABLE IF NOT EXISTS types_of_question(id INT, type VARCHAR(50), PRIMARY KEY (id))""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS ranking_table(id_of_poll INT, vector_of_poll BLOB, 
        PRIMARY KEY (id_of_poll), 
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS private_polls(id_of_poll INT, code VARCHAR(15) UNIQUE,
        PRIMARY KEY (id_of_poll), 
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS cover_of_polls(cover MEDIUMBLOB, id_of_poll INT PRIMARY KEY,
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")

        # users
        # id_of_user состоит из последовательности длинной 6 цифр со знаком минус
        connection_object.cursor.execute(
            """CREATE TABLE IF NOT EXISTS table_of_type_of_users(id_of_type INT, type VARCHAR(100), PRIMARY KEY (id_of_type))""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS users(id_of_user INT AUTO_INCREMENT, type_of_user INT, 
        PRIMARY KEY (id_of_user),
        FOREIGN KEY (type_of_user) REFERENCES table_of_type_of_users(id_of_type) ON UPDATE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS user(id_of_user INT, password VARCHAR(255), login VARCHAR(100), nickname VARCHAR(50), tags VARCHAR(100), date_of_birth DATE, number_of_phone VARCHAR(17),
        PRIMARY KEY (id_of_user), 
        FOREIGN KEY (id_of_user) REFERENCES users(id_of_user) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS sessions(id_of_user INT, id_of_cookie INT, cookie VARCHAR(30), expired TIMESTAMP, name_of_cookie VARCHAR(30), 
        PRIMARY KEY (id_of_cookie), 
        FOREIGN KEY (id_of_user) REFERENCES users (id_of_user) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS pow_table(pow INT, cookie VARCHAR(10))""")
        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS ranking_table_of_users(id_of_user INT PRIMARY KEY, vector_of_user BLOB,
        FOREIGN KEY (id_of_user) REFERENCES users (id_of_user) ON DELETE CASCADE)""")

        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS ban_users(id_of_user INT PRIMARY KEY)""")

        # superuser
        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS superusers(id_of_superuser INT, login VARCHAR(100), password VARCHAR(255), 
        PRIMARY KEY (id_of_superuser), 
        FOREIGN KEY (id_of_superuser) REFERENCES users (id_of_user) ON DELETE CASCADE)""")
        # данные, которые пользователь ввел в ответах на опрос
        connection_object.cursor.execute("""CREATE TABLE IF NOT EXISTS table_of_users_who_pass_the_poll(id_of_user INT, id_of_poll INT, 
        PRIMARY KEY (id_of_user, id_of_poll), 
        FOREIGN KEY (id_of_user) REFERENCES users (id_of_user) ON DELETE CASCADE, 
        FOREIGN KEY (id_of_poll) REFERENCES polls (id) ON DELETE CASCADE)""")
        connection_object.cursor.execute(
            """CREATE TABLE IF NOT EXISTS data_of_passing_poll_from_user(id INT AUTO_INCREMENT, id_of_poll INT, id_of_user INT, serial_number_of_question INT, type_of_question VARCHAR(50), value TEXT, PRIMARY KEY (id))""")
        connection_object.connection.commit()

        self.set_types_of_questions()
        self.set_table_type_of_users()
        self.create_superuser()

    # -----------------------------------------------------------------------------------------------------------------------
    # часть кода связанная с методами базы данных: подключение, переподключение, удаление таблиц
    @get_connection_and_cursor
    def delete_tables(self, connection_object: ConnectionAndCursor = None):
        """
        Функция нужна для удаления таблиц в БД

        :return: None
        """
        connection_object.cursor.execute("""DROP TABLE polls, questions, options, rightAnswers""")
        connection_object.connection.commit()


client_mysqldb = MysqlDB()