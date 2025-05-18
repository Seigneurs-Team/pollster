from drf_spectacular.utils import OpenApiResponse
from Configs.Serializers.admin_panel import SuccessResponseOnGetAdminPanel


GET_ADMIN_PANEL_SCHEMA = {
    'summary': 'Получение страницы Админ-панели.',
    'description': 'Endpoint нужен для получения Админ-панели и реализации на ней функций Администратора.',
    'methods': ['GET'],
    'tags': ['Admin panel'],
    'responses': {
        200: OpenApiResponse(
            description='Сервер обработал запрос и вернул страницу Админ-панели.',
            response=SuccessResponseOnGetAdminPanel
        )
    }
}