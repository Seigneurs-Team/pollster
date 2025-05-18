from rest_framework import serializers


class SuccessDeletePoll(serializers.Serializer):
    response = serializers.CharField(default='Опрос был успешно удален.')


class UnSuccessDeletePoll404(serializers.Serializer):
    response = serializers.CharField(default='Данный опрос не найден.')