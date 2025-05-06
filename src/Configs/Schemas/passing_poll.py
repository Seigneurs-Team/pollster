from drf_spectacular.utils import OpenApiResponse, OpenApiParameter


PASSING_POLL_PAGE_SCHEMA = {
    'summary': 'Получение страницы прохождения опроса',
    'tags': ['passing poll'],
    'methods': ['GET'],
    'description': 'Endpoint необходим для получения страницы прохождения опроса, чтобы пользователь мог пройти опрос. Требует наличие авторизации в системе.',
    'responses': {
        200: OpenApiResponse(
            description='Запрос был успешно обработан. Сервер возвращает в ответе страницу для прохождения опроса.'
        ),
        302: OpenApiResponse(
            description='Пройти опрос попытался неавторизованный пользователь. Он будет переадресован на страницу входа в аккаунт.'
        ),
    }
}