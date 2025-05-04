from drf_spectacular.utils import OpenApiResponse, OpenApiParameter
from Configs.Serializers.main_page import ListOfPolls


MAIN_PAGE_SCHEMA = {
    'summary': 'получение главной страницы',
    'tags': ['main page'],
    'description': 'Endpoint нужен для получения HTML главной страницы, а также получения рекомендательных опросов, если пользователь авторизован в системе.',
    'methods': ['GET'],
    'responses': {
        200: OpenApiResponse(description='Запрос успешно был обработан. Выдан HTML главной страницы.')
    }
}


GET_POLLS_SCHEMA = {
    'summary': 'Получение списка опросов из БД.',
    'description': 'Endpoint нужен для выборки n-го количества опросов из БД MySQL.',
    'tags': ['main page'],
    'parameters': [
        OpenApiParameter(
            name='num_of_polls',
            location=OpenApiParameter.PATH,
            description='Параметр обозначает количество опросов, которые необходимо вернуть.',
            required=False,
            type=int
        )
    ],
    'responses': {
        200: OpenApiResponse(
            description='Список опросов.',
            response=ListOfPolls
        )
    }
}