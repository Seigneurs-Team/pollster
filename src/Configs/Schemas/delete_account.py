from drf_spectacular.utils import OpenApiResponse

from Configs.Serializers.delete_account import ResponseDeleteAccount


DELETE_ACCOUNT_SCHEMA = {
    'summary': 'удаление пользователя.',
    'tags': ['delete account'],
    'description': 'Endpoint нужен для удаления пользователя из системы. Это значит также удаление всех зависимых записей от этого пользователя в БД.',
    'methods': ['DELETE'],
    'responses': {
        200: OpenApiResponse(
            description='Запрос успешно обработан. Пользователь удален из системы.',
            response=ResponseDeleteAccount
        ),
        302: OpenApiResponse(
            description='Пользователь не авторизован в систему и будет перенаправлен на страницу авторизации.'
        )
    }
}