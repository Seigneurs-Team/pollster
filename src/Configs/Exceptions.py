class NotFoundPoll(Exception):
    def __init__(self, message):
        super().__init__(message)


class ErrorSameLogins(Exception):
    def __init__(self, message):
        super().__init__(message)


class NotFoundCookieIntoPowTable(Exception):
    def __init__(self, message):
        super(NotFoundCookieIntoPowTable, self).__init__(message)


class CookieWasExpired(Exception):
    def __init__(self, message):
        super(CookieWasExpired, self).__init__(message)


class RepeatPollError(Exception):
    def __init__(self, message):
        super(RepeatPollError, self).__init__(message)