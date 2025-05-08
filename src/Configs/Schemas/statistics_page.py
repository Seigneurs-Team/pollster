from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample

from Configs.Serializers.statistics_page import (
    SuccessResponseOnStatisticsPage,
    SuccessResponseOnStatisticsPagePrivatePoll
)

import json

STATISTICS_PAGE_SCHEMA = {
    'summary': 'Получение страницы статистики опроса.',
    'description': 'Endpoint нужен для получения страницы статистики опроса. Статистику опроса может посмотреть как любой авторизованный пользователь, так и только автор данного опроса.',
    'tags': ['statistics page'],
    'parameters': [
        OpenApiParameter(
            name='id_of_poll',
            description='Параметр обозначает идентификатор опроса, коего требуется посмотреть статистику.',
            location=OpenApiParameter.PATH,
            required=True,
            type=int
        )
    ],
    'responses': {
        200: OpenApiResponse(
            description='Сервер обработал запрос и выдал HTML страницу со следующими параметрами.',
            response=SuccessResponseOnStatisticsPage,
            examples=[
                OpenApiExample(
                    name='Приватный опрос.',
                    value=SuccessResponseOnStatisticsPagePrivatePoll().data
                ),
                OpenApiExample(
                    name='Опрос неприватный.',
                    value=SuccessResponseOnStatisticsPage().data
                )
            ]
        ),
        403: OpenApiResponse(
            description='Не автор приватного опроса попытался посмотреть статистику. Он будет переадресован на страницу входа в профиль.'
        ),
        302: OpenApiResponse(
            description='Неавторизованный пользователь попытался посмотреть статистику опроса.'
        )
    },
}


GET_STATISTICS_SCHEMA = {
    'summary': 'Получение всей статистики опроса.'
}