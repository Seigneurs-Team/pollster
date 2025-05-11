from rest_framework import serializers

from Configs.Serializers.main_page import Poll


class RequestOnSearchPolls(serializers.Serializer):
    name_of_poll = serializers.CharField()
    tags = serializers.ListField()


class SuccessResponseOnSearchPolls(serializers.Serializer):
    list_of_polls = serializers.ListField(child=Poll())