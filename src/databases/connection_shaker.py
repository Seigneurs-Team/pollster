import dataclasses
import mysql.connector


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