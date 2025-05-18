from rest_framework import serializers

from Configs.Serializers.main_page import Poll


class SuccessResponseOnGetAdminPanel(serializers.Serializer):
    all_objects = serializers.ListField(child=Poll())


class SuccessResponseOnBanUser(serializers.Serializer):
    response = serializers.CharField(default='Пользователь успешно заблокирован в системе.')


class UnSuccessResponseOnBanUser404(serializers.Serializer):
    response = serializers.CharField(default='Пользователь не найден.')


class SuccessUnBanUser(serializers.Serializer):
    response = serializers.CharField(default='Пользователь успешно разблокирован в системе.')