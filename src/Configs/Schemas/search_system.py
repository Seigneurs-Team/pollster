from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

from Configs.Serializers.search_system import RequestOnSearchPolls, SuccessResponseOnSearchPolls


SEARCH_POLLS_SCHEMA = {
    'summary': 'Поиск опросов по тегам и названиям.',
    'description': 'Данный Endpoint необходим для поиска опросов по их тегам и названиям.',
    'methods': ['GET'],
    'tags': ['main page', 'search polls'],
    'request': RequestOnSearchPolls,
    'parameters': [
        OpenApiParameter(
            name='count_of_polls',
            description='Параметр определяет количество опросов, которые будут возвращены с сервера.',
            type=int,
            location=OpenApiParameter.PATH,
            required=True
        )
    ],
    'responses': {
        200: OpenApiResponse(
            description='Сервер успешно обработал запрос и выслал те опросы, которые наиболее подходят к заданному поиску.',
            response=SuccessResponseOnSearchPolls
        ),
        302: OpenApiResponse(
            description='Запрос совершил неавторизованный пользователь и будет переадресован на страницу входа в профиль.'
        )

    }
}