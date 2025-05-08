from drf_spectacular.utils import OpenApiResponse

from Configs.Serializers.sign_in import (
    RequestOnSignIn,
    SuccessResponseOnSignIn,
    UnSuccessResponseOnSignIn400,
    UnSuccessResponseOnSignIn401
)


SIGN_IN_PAGE_SCHEMA = {
    'summary': 'Получение страницы входа в аккаунт.',
    'tags': ['sign in'],
    'description': "Endpoint нужен для получения страницы входа в аккаунт.",
    'responses': {
        200: OpenApiResponse(
            description='Сервер обработал запрос и отослал страницу входа в аккаунт'
        )
    }
}


SIGN_IN_SCHEMA = {
    'summary': 'Авторизация в системе',
    'tags': ['sign in'],
    'description': 'Endpoint нужен для авторизации пользователя в системе',
    'request': RequestOnSignIn,
    'responses': {
        200: OpenApiResponse(
            description='Пользователь успешно авторизовался в системе.',
            response=SuccessResponseOnSignIn
        ),
        400: OpenApiResponse(
            description='Не было пройдено испытание POW.',
            response=UnSuccessResponseOnSignIn400
        ),
        401: OpenApiResponse(
            description='Пользователь ввел неверные учетные записи.',
            response=UnSuccessResponseOnSignIn401
        )
    }
}