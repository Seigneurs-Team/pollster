from drf_spectacular.utils import OpenApiResponse, OpenApiParameter
from Configs.Serializers.profile_page import SuccessResponseOnGetProfilePage


PROFILE_PAGE_SCHEMA = {
    'summary': 'Получение HTML страницы профиля пользователя.',
    'tags': ['profile page'],
    'description': 'Endpoint нужен для получения HTML страницы профиля пользователя. В этом ответе также находятся опросы, созданные и пройденные пользователем.',
    'parameters': [
        OpenApiParameter(
            name='id_of_user',
            location=OpenApiParameter.PATH,
            description='Параметр обозначает идентификатор пользователя.',
            required=True,
            type=int
        )
    ],
    'responses': {
        200: OpenApiResponse(
            description='Запрос был успешно обработан и была выдана HTML страница со следующими параметрами.',
            response=SuccessResponseOnGetProfilePage
        )
    }
}