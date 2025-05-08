from rest_framework import serializers


class RequestOnSignIn(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()
    pow = serializers.CharField()


class SuccessResponseOnSignIn(serializers.Serializer):
    response = serializers.CharField(default='Пользователь успешно авторизован в системе.')


class UnSuccessResponseOnSignIn401(serializers.Serializer):
    response = serializers.CharField(default='Неверный пароль или почта.')


class UnSuccessResponseOnSignIn400(serializers.Serializer):
    response = serializers.CharField(default='Неправильный pow в теле запроса. Challenge POW не был пройден правильно.')
