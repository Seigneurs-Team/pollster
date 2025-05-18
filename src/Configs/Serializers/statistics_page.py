from rest_framework import serializers


class StatisticsTextAnswer(serializers.Serializer):
    text = serializers.CharField()


class SttisticsOption(serializers.Serializer):
    count_of_selected = serializers.IntegerField()
    is_right_answer = serializers.BooleanField()


class StatisticsQuestion(serializers.Serializer):
    id = serializers.IntegerField()
    type_of_question = serializers.CharField()
    text_of_question = serializers.CharField()
    serial_number = serializers.IntegerField()
    options = serializers.ListField(child=SttisticsOption())
    text_answers = serializers.ListField(child=StatisticsTextAnswer())
    right_text_answer = serializers.CharField()
    wrong_text_answers = serializers.ListField(child=StatisticsTextAnswer())


class Statistics(serializers.Serializer):
    count_of_user = serializers.IntegerField()
    name_of_poll = serializers.CharField()
    description_of_poll = serializers.CharField()
    tags_of_poll = serializers.ListField()
    author = serializers.CharField()
    questions = serializers.ListField(child=StatisticsQuestion())


class UserInStatistics(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class SuccessResponseOnStatisticsPage(serializers.Serializer):
    id_of_poll = serializers.IntegerField()
    user = UserInStatistics()
    questions = Statistics()
    cover = serializers.CharField()


class SuccessResponseOnStatisticsPagePrivatePoll(SuccessResponseOnStatisticsPage):
    qr_code = serializers.CharField()
    url_on_poll = serializers.CharField()