from rest_framework import serializers
from Configs.Serializers.statistics_page import UserInStatistics


class Question(serializers.Serializer):
    text = serializers.CharField()
    type = serializers.CharField()
    id = serializers.IntegerField()
    rightAnswer = serializers.CharField()
    options = serializers.ListField()
    rightAnswersId = serializers.ListField(child=serializers.IntegerField())


class DataOfPoll(serializers.Serializer):
    private = serializers.BooleanField(default=False)
    name_of_poll = serializers.CharField()
    tags = serializers.ListField()
    description = serializers.CharField()
    questions = serializers.ListField(child=Question())
    cover = serializers.CharField()
    coverDefault = serializers.IntegerField()
    id_of_poll = serializers.IntegerField()


class SuccessCreatePoll(serializers.Serializer):
    response = serializers.CharField(default='Опрос был успешно создан.')


class UnSuccessCreatePoll500(serializers.Serializer):
    response = serializers.CharField(default='Опрос не был создан.')


class UnSuccessCreatePoll400(serializers.Serializer):
    response = serializers.CharField(default='Неправильные входные данные.')


class UnSuccessCreatePoll403(serializers.Serializer):
    response = serializers.CharField(default='Попытка XSS атаки на систему.')


class ResponseOnGetCreatePollPage(serializers.Serializer):
    user = UserInStatistics()
    tags = serializers.ListField()