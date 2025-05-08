from rest_framework import serializers


class SuccessPassingPoll(serializers.Serializer):
    response = serializers.CharField(default='Данные были успешно сохранены в БД.')


class ResponseONXSS(serializers.Serializer):
    response = serializers.CharField(default='Неправильные типы вопросов были отправлены на сервер.')


class ResponseOnRepeatPoll(serializers.Serializer):
    response = serializers.CharField(default='Вы уже прошли данный опрос.')