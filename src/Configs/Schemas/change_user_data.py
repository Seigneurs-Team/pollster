from drf_spectacular.utils import OpenApiResponse, OpenApiParameter
from Configs.Serializers.change_user_data import ChangeNicknameSerializer, SuccessChangeSerializer, UnSuccessChangeSerializer


CHANGE_NICKNAME_SCHEMA = {
    'summary': 'Изменение никнейма пользователя.',
    'description': 'Endpoint необходим для для изменения никнейма пользователя в БД.',
    'request': ChangeNicknameSerializer,
    'responses': {
        200: OpenApiResponse(
            description='Данные успешно сохранены',
            response=SuccessChangeSerializer
        ),
        400: OpenApiResponse(
            description='Некорректные данные в JSON.',
            response=UnSuccessChangeSerializer
        )
    }
}