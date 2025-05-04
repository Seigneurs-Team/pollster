from rest_framework import serializers


class ChangeNicknameSerializer(serializers.Serializer):
    nickname = serializers.CharField()


class SuccessChangeSerializer(serializers.Serializer):
    response = serializers.IntegerField(min_value=200)


class UnSuccessChangeSerializer(serializers.Serializer):
    response = serializers.CharField()