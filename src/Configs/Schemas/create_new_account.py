from drf_spectacular.utils import OpenApiResponse
from Configs.Serializers.create_new_account import (
    NewAccountData,
    ResponseOf400FromCreateNewAccount,
    ResponseOf409FromCreateNewAccount,
    ResponseOf401FromCreateNewAccount,
    ChallengeData
)


CREATE_NEW_ACCOUNT_PAGE_SCHEMA = {
    'summary': 'Получение страницы создания нового аккаунта в системе.',
    'tags': ['create new account'],
    'description': 'Endpoint нужен для получения HTML страницы создания нового аккаунта в системе.',
    'methods': ['GET'],
    'responses': {
        200: OpenApiResponse(description='Запрос успешно обработан. Выдан HTML страницы создания аккаунта, а также специальный куки "auth_sessionid" для продолжения создания аккаунта в системе.')
    }
}


CREATE_NEW_ACCOUNT_SCHEMA = {
    'summary': 'Создание нового пользователя в системе.',
    'tags': ['create new account'],
    'description': 'Endpoint нужен для создания пользователя в БД, а далее выдача ему полномочий.',
    'methods': ['POST'],
    'request': NewAccountData,
    'responses': {
        200: OpenApiResponse(description='Пользователь успешно создался в БД и пользователь имеет авторизованные куки, с которыми он может дальше работать в системе'),
        400: OpenApiResponse(description='Не найдено значение pow в запросе либо не найден куки файл.', response=ResponseOf400FromCreateNewAccount),
        409: OpenApiResponse(description='Данный логин уже занят.', response=ResponseOf409FromCreateNewAccount),
        401: OpenApiResponse(description='Недействительный куки', response=ResponseOf401FromCreateNewAccount)
    }
}

GET_CHALLENGE_SCHEMA = {
    'summary': 'Получение данных для POW испытания',
    'tags': ['create new account'],
    'description': 'Endpoint нужен для получения информации испытания. Это испытание нужно для проверки на то, что запрос производит реальный человек, а не бот.',
    'methods': ['GET'],
    'responses': {
        200: OpenApiResponse(description='Данные для прохождения POW испытания', response=ChallengeData),
        403: OpenApiResponse(description='Не найден куки "auth_sessionid" в запросе')
    }
}