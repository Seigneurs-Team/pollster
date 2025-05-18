from rest_framework import serializers

from Configs.Serializers.statistics_page import UserInStatistics


class QuestionPassingPoll(serializers.Serializer):
    text = serializers.CharField()
    type = serializers.CharField()
    id = serializers.IntegerField()
    shortTextRightAnswer = serializers.CharField()
    options = serializers.ListField()
    rightAnswersId = serializers.ListField(child=serializers.IntegerField())


class DataOfPollPassingPoll(serializers.Serializer):
    name_of_poll = serializers.CharField()
    tags = serializers.ListField()
    description = serializers.CharField()
    questions = serializers.ListField(child=QuestionPassingPoll())
    cover = serializers.CharField()


class SuccessPassingPoll(serializers.Serializer):
    response = serializers.CharField(default='Данные были успешно сохранены в БД.')


class ResponseONXSS(serializers.Serializer):
    response = serializers.CharField(default='Неправильные типы вопросов были отправлены на сервер.')


class ResponseOnRepeatPoll(serializers.Serializer):
    response = serializers.CharField(default='Вы уже прошли данный опрос.')


class ResponseOnGetPassingPollPage(serializers.Serializer):
    user = UserInStatistics()
    poll = DataOfPollPassingPoll()
    is_pass = serializers.BooleanField()