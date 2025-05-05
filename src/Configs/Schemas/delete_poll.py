from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

from Configs.Serializers.delete_poll import SuccessDeletePoll, UnSuccessDeletePoll404


DELETE_POLL_SCHEMA = {
    'summary': 'Удаление опроса из БД.',
    'tags': ['delete poll', 'profile page'],
    'description': 'Endpoint нужен для удаления опроса из БД, а также связанных с ним записей.',
    'methods': ['DELETE'],
    'parameters': [
        OpenApiParameter(
            name='id_of_poll',
            location=OpenApiParameter.PATH,
            description='Параметр обозначает идентификатор опроса, который необходимо удалить',
            required=True,
            type=int
        )
    ],
    'responses': {
        200: OpenApiResponse(
            description='Опрос был успешно удален.',
            response=SuccessDeletePoll
        ),
        403: OpenApiResponse(
            description='Посторонний пользователь пытается удалить опрос другого пользователя.'
        ),
        404: OpenApiResponse(
            description='Данный опрос не найден.',
            response=UnSuccessDeletePoll404
        )
    }
}