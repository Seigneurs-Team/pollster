from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

from Configs.Serializers.get_qr_code import SuccessResponseOfGetQRCode


GET_QR_CODE_SCHEMA = {
    'summary': 'Получение QR кода ссылки опроса, а также саму ссылку.',
    'tags': ['get qr code', 'profile page'],
    'description': 'Endpoint нужен для получения QR кода, как обычного опроса, так и приватного.',
    'methods': ['GET'],
    'parameters': [
        OpenApiParameter(
            name='id_of_poll',
            location=OpenApiParameter.PATH,
            description='Параметр обозначает идентификатор опроса, который необходимо удалить.',
            required=True,
            type=int
        )
    ],
    'responses': {
        200: OpenApiResponse(
            description='Запрос был успешно обработан и был выслан ответ.',
            response=SuccessResponseOfGetQRCode
        ),
        302: OpenApiResponse(
            description='Запрос сделал неавторизованный пользователь и был перенаправлен на страницу авторизации.'
        ),
        403: OpenApiResponse(
            description='Пользователь попытался добыть код приватного опроса через получение QR кода.'
        )
    }
}