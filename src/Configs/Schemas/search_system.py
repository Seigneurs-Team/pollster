from drf_spectacular.utils import OpenApiResponse

from Configs.Serializers.search_system import (
    RequestOnSearchPolls,
    SuccessResponseOnSearchPolls,
    UnSuccessResponseOnSearchPolls400
)


SEARCH_POLLS_SCHEMA = {
    'summary': 'Поиск опросов по тегам и названиям.',
    'description': 'Данный Endpoint необходим для поиска опросов по их тегам и названиям.',
    'methods': ['POST'],
    'tags': ['main page', 'search polls'],
    'request': RequestOnSearchPolls,
    'responses': {
        200: OpenApiResponse(
            description='Сервер успешно обработал запрос и выслал те опросы, которые наиболее подходят к заданному поиску.',
            response=SuccessResponseOnSearchPolls
        ),
        302: OpenApiResponse(
            description='Запрос совершил неавторизованный пользователь и будет переадресован на страницу входа в профиль.'
        ),
        400: OpenApiResponse(
            description='Неправильные поля для поиска были указаны в теле запроса.',
            response=UnSuccessResponseOnSearchPolls400
        )

    }
}