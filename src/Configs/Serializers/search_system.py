from rest_framework import serializers

from Configs.Serializers.main_page import Poll


class RequestOnSearchPolls(serializers.Serializer):
    name_of_poll_for_search = serializers.CharField()
    tags = serializers.ListField()
    watched_polls = serializers.ListField(child=serializers.IntegerField())

    count_of_polls = serializers.IntegerField(default=10, min_value=1)


class SuccessResponseOnSearchPolls(serializers.Serializer):
    list_of_polls = serializers.ListField(child=Poll())


class UnSuccessResponseOnSearchPolls400(serializers.Serializer):
    response = serializers.CharField(default='Неправильные поля в теле запроса.')