from drf_spectacular.utils import OpenApiResponse

from Configs.Serializers.log_out import SuccessLogOut


LOG_OUT_SCHEMA = {
    'summary': 'Выход из аккаунта.',
    'description': 'Endpoint нужен для выхода пользователя из своего аккаунта. Под этим тезисом понимается удаление в БД записи с куки файлом, отвечающим за аутентификацию пользователя в системе.',
    'tags': ['profile page'],
    'methods': ['POST'],
    'responses': {
        200: OpenApiResponse(
            description='Пользователь успешно вышел из аккаунта',
            response=SuccessLogOut
        ),
        302: OpenApiResponse(
            description='Выйти из аккаунта попытался неавторизованный пользователь в системе, поэтому он будет переадресован на адрес "/sign_in".'
        )
    }
}