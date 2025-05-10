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

    num_of_right_answers = serializers.IntegerField()
    num_of_wrong_answers = serializers.IntegerField()

    count_of_writes = serializers.IntegerField()


class SuccessResponseOnGetStatistics(serializers.Serializer):
    count_of_user = serializers.IntegerField()
    name_of_poll = serializers.CharField()
    description_of_poll = serializers.CharField()
    tags_of_poll = serializers.ListField()
    author = serializers.CharField()
    questions = serializers.ListField(child=Question())
