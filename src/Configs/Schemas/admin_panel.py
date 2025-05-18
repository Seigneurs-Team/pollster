from drf_spectacular.utils import OpenApiResponse
from Configs.Serializers.admin_panel import (
    SuccessResponseOnGetAdminPanel,
    SuccessResponseOnBanUser,
    UnSuccessResponseOnBanUser404,
    SuccessUnBanUser
)


GET_ADMIN_PANEL_SCHEMA = {
    'summary': 'Получение страницы Админ-панели.',
    'description': 'Endpoint нужен для получения Админ-панели и реализации на ней функций Администратора.',
    'methods': ['GET'],
    'tags': ['Admin panel'],
    'responses': {
        200: OpenApiResponse(
            description='Сервер обработал запрос и вернул страницу Админ-панели.',
            response=SuccessResponseOnGetAdminPanel
        ),
        403: OpenApiResponse(
            description='Попытка не супер пользователя получить доступ к админ-панели.'
        )
    }
}


BAN_USER_SCHEMA = {
    'summary': 'Блокировка аккаунта пользователя.',
    'description': 'Endpoint нужен для блокировки пользователя в системе.',
    'methods': ['POST'],
    'tags': ['Admin panel'],
    'responses': {
        200: OpenApiResponse(
            description='Пользователь успешно заблокирован в системе.',
            response=SuccessResponseOnBanUser
        ),
        404: OpenApiResponse(
            description='Пользователь не найден.',
            response=UnSuccessResponseOnBanUser404
        ),
        403: OpenApiResponse(
            description='Попытка не супер пользователя получить доступ к админ-панели.'
        )
    }
}


UNBAN_SCHEMA = {
    'summary': 'Разблокировка аккаунта пользователя.',
    'description': 'Endpoint нужен для разблокировки пользователя в системе.',
    'methods': ['POST'],
    'tags': ['Admin panel'],
    'responses': {
        200: OpenApiResponse(
            description='Пользователь успешно разблокирован в системе.',
            response=SuccessUnBanUser
        ),
        404: OpenApiResponse(
            description='Пользователь не найден.',
            response=UnSuccessResponseOnBanUser404
        ),
        403: OpenApiResponse(
            description='Попытка не супер пользователя получить доступ к админ-панели.'
        )
    }
}