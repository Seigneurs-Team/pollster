from rest_framework import serializers


class SuccessLogOut(serializers.Serializer):
    response = serializers.CharField(default='Пользователь успешно вышел из аккаунта.')