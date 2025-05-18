from drf_spectacular.utils import OpenApiResponse
from Configs.Serializers.change_user_data import (
    SuccessChangeSerializer,
    UnSuccessChangeSerializer,
)


def get_change_data_of_user_schema(serializer):
    change_data_of_user_schema = {
        'summary': 'Изменение данных пользователя.',
        'description': 'Endpoint необходим для для изменения данных пользователя в БД.',
        'request': serializer,
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
    return change_data_of_user_schema


