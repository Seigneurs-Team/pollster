from mysql.connector import connect
import mysql
import logging
from Configs.Hosts import Hosts
from Configs.Poll import Poll
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
        except mysql.connector.errors.ProgrammingError:
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
        self.connection.commit()

    def get_polls(self, num_of_polls: int = 1) -> list:
        self.cursor.execute("""SELECT * FROM polls""")
        result = self.cursor.fetchmany(num_of_polls)
        return result

    def create_poll(self, poll: Poll):
        try:
            self.cursor.execute("""INSERT INTO polls(id, tags, name_of_poll, description) VALUES (%s, %s, %s, %s)""", (poll.id, poll.tags, poll.name_of_poll, poll.description))
            self.connection.commit()
            return True
        except:
            return False

    def reconnect(self):
        self.connection, self.cursor = self.connect_to_db()


client_mysqldb = MysqlDB()