from rest_framework import serializers


class TextAnswer(serializers.Serializer):
    text = serializers.CharField()


class Option(serializers.Serializer):
    count_of_selected = serializers.IntegerField()
    is_right_answer = serializers.BooleanField()


class Question(serializers.Serializer):
    id = serializers.IntegerField()
    type_of_question = serializers.CharField()
    text_of_question = serializers.CharField()
    serial_number = serializers.IntegerField()
    options = serializers.ListField(child=Option())
    text_answers = serializers.ListField(child=TextAnswer())
    right_text_answer = serializers.CharField()
    wrong_text_answers = serializers.ListField(child=TextAnswer())


class Statistics(serializers.Serializer):
    count_of_user = serializers.IntegerField()
    name_of_poll = serializers.CharField()
    description_of_poll = serializers.CharField()
    tags_of_poll = serializers.ListField()
    author = serializers.CharField()
    questions = serializers.ListField(child=Question())


class User(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class SuccessResponseOnStatisticsPage(serializers.Serializer):
    id_of_poll = serializers.IntegerField()
    user = User()
    questions = Statistics()


class SuccessResponseOnStatisticsPagePrivatePoll(SuccessResponseOnStatisticsPage):
    qr_code = serializers.CharField()
    url_on_poll = serializers.CharField()



print(SuccessResponseOnStatisticsPage().fields)