class NotFoundPoll(Exception):
    """
    Класс определяет ошибку "не найден опрос в системе"
    """
    def __init__(self, message):
        super().__init__(message)


class ErrorSameLogins(Exception):
    """
    Класс определяет ошибку "одинаковые логины"
    """
    def __init__(self, message):
        super().__init__(message)


class NotFoundCookieIntoPowTable(Exception):
    """
    Класс определяет ошибку "не найдена запись с таким куки в БД"
    """
    def __init__(self, message):
        super(NotFoundCookieIntoPowTable, self).__init__(message)


class CookieWasExpired(Exception):
    """
    Класс определяет ошибку "время жизни куки истекло"
    """
    def __init__(self, message):
        super(CookieWasExpired, self).__init__(message)


class RepeatPollError(Exception):
    """
    Куки определяет ошибку "повторение прохождения опроса"
    """
    def __init__(self, message):
        super(RepeatPollError, self).__init__(message)


class TryToXSS(Exception):
    """
    Класс маркирует попытку XSS атаки
    """
    def __init__(self, message):
        super(TryToXSS, self).__init__(message)
        
        
class WronglyResponse(Exception):
    """
    Класс определяет то, что контейнер rabbitmq возвращает ошибку
    """
    def __init__(self, message):
        super(WronglyResponse, self).__init__(message)


class ConnectionRefused(Exception):
    """
    Класс определяет, что соединение с контейнером было потеряно
    """
    def __init__(self, message):
        super(ConnectionRefused, self).__init__(message)