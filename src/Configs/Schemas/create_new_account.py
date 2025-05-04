from drf_spectacular.utils import OpenApiResponse, OpenApiParameter


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
    'request': {}
}