from drf_spectacular.utils import OpenApiResponse, OpenApiExample

from Configs.Serializers.create_poll import (
    DataOfPoll,
    SuccessCreatePoll,
    UnSuccessCreatePoll500,
    UnSuccessCreatePoll400,
    UnSuccessCreatePoll403
)


CREATE_POLL_PAGE_SCHEMA = {
    'summary': 'Получение страницы создания опроса',
    'tags': ['create poll'],
    'description': 'Endpoint нужен для получения страницы создания опроса, которая впоследствии будет необходима пользователю для создания сущности опроса',
    'methods': ['GET'],
    'responses': {
        200: OpenApiResponse(description='Запрос был успешно обработан. Выдан HTML страницы создания опроса.'),
        302: OpenApiResponse(description='Куки auth_sessionid оказался невалидным. Необходимо пройти авторизацию. Происходит перенаправление пользователя на страницы /sign_in')
    }
}


CREATE_POLL_SCHEMA = {
    'summary': 'Создание опроса.',
    'description': 'Endpoint нужен для создания опроса и его сохранения в БД.',
    'tags': ['create poll'],
    'methods': ['POST'],
    'request': DataOfPoll,
    'responses': {
        200: OpenApiResponse(
            description='Опрос был успешно создан.',
            response=SuccessCreatePoll,
            examples=[
                    OpenApiExample(
                        'Пример с private=True',
                        value={
                            'response': 'string',
                            'qr_code': 'string',
                            'url': 'string'
                        }
                    ),
                    OpenApiExample(
                        'Пример с private=False',
                        value={
                            'response': 'string',
                        }
                    )
                ]
        ),
        500: OpenApiResponse(
            description='Опрос не был успешно создан. Проблема на backend стороне.',
            response=UnSuccessCreatePoll500
        ),
        400: OpenApiResponse(
            description='Сервер получил неверные входные данные.',
            response=UnSuccessCreatePoll400
        ),
        403: OpenApiResponse(
            description='Была предпринята попытка XSS атаки на систему.',
            response=UnSuccessCreatePoll403
        )
    },
}