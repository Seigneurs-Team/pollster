from rest_framework import serializers


class Poll(serializers.Serializer):
    name_of_poll = serializers.CharField()
    description = serializers.CharField()
    tags = serializers.ListField()
    id_of_poll = serializers.IntegerField()
    id_of_author = serializers.IntegerField()
    nickname_of_author = serializers.CharField()
    cover = serializers.CharField()


class ListOfPolls(serializers.Serializer):
    list = serializers.ListField(child=Poll())


class User(serializers.Serializer):
    is_authenticated = serializers.BooleanField()
    id = serializers.IntegerField()
    username = serializers.CharField()


class ResponseOnMainPage(serializers.Serializer):
    all_objects = serializers.ListField(child=Poll())
    tags = serializers.ListField()
    user = User()