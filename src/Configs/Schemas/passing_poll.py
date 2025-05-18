from drf_spectacular.utils import OpenApiResponse
from Configs.Serializers.passing_poll import (
    SuccessPassingPoll,
    ResponseONXSS,
    ResponseOnRepeatPoll,
    ResponseOnGetPassingPollPage
)


PASSING_POLL_PAGE_SCHEMA = {
    'summary': 'Получение страницы прохождения опроса',
    'tags': ['passing poll'],
    'methods': ['GET'],
    'description': 'Endpoint необходим для получения страницы прохождения опроса, чтобы пользователь мог пройти опрос. Требует наличие авторизации в системе.',
    'responses': {
        200: OpenApiResponse(
            description='Запрос был успешно обработан. Сервер возвращает в ответе страницу для прохождения опроса.',
            response=ResponseOnGetPassingPollPage
        ),
        302: OpenApiResponse(
            description='Пройти опрос попытался неавторизованный пользователь. Он будет переадресован на страницу входа в аккаунт.'
        ),
    }
}


PASSING_POLL_SCHEMA = {
    'summary': 'Отправка данных, которые пользователь ввел на странице прохождения опроса.',
    'tags': ['passing poll'],
    'methods': ['POST'],
    'description': 'Endpoint необходим для сохранения данных в БД, которые пользователь ввел на странице прохождения опроса.',
    'responses': {
        200: OpenApiResponse(
            description='Данные были успешно сохранены в БД.',
            response=SuccessPassingPoll
        ),
        400: OpenApiResponse(
            description='Неправильные типы вопросов были переданы в POST запросе.',
            response=ResponseONXSS
        ),
        403: OpenApiResponse(
            description='Попытка прохождения опроса два раза.',
            response=ResponseOnRepeatPoll
        )
    }
}