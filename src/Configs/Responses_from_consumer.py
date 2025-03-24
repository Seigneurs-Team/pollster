from dataclasses import dataclass


@dataclass
class Responses:
    Ok: str = 'OK'
    NotFoundPoll: str = 'Not found the poll'
    PollIsExists: str = 'Poll is exists in table'
    UserPassAllPolls: str = 'Все опросы пройдены пользователем'
    UserIsExists: str = 'User is exists in the table'
    NotFoundUser: str = 'Не найден пользователь'
    NotValidData: str = 'Неправильная структура тегов'