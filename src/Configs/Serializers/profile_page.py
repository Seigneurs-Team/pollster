from rest_framework import serializers
from Configs.Serializers.main_page import Poll


class User(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    phone = serializers.CharField()
    date_of_birth = serializers.DateField()
    tags_of_user = serializers.ListField()
    userPolls = serializers.ListField(child=Poll())
    completedPolls = serializers.ListField(child=Poll())


class SuccessResponseOnGetProfilePage(serializers.Serializer):
    user = User()
    tags = serializers.ListField()


