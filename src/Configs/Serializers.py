from rest_framework import serializers


class Poll(serializers.Serializer):
    name_of_poll = serializers.CharField()
    description = serializers.CharField()
    tags = serializers.CharField()
    id_of_poll = serializers.IntegerField()
    id_of_author = serializers.IntegerField()
    nickname_of_author = serializers.CharField()
    cover = serializers.CharField()


class ListOfPolls(serializers.Serializer):
    list = serializers.ListField(child=Poll())