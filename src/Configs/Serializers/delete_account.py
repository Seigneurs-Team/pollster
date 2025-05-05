from rest_framework import serializers


class ResponseDeleteAccount(serializers.Serializer):
    response = serializers.CharField(default='Учетная запись успешно удалена.')