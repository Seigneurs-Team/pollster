from rest_framework import serializers


class ChangeNicknameSerializer(serializers.Serializer):
    nickname = serializers.CharField()


class ChangeEmailSerializer(serializers.Serializer):
    email = serializers.CharField()


class ChangeDateOfBirthSerializer(serializers.Serializer):
    date_of_birth = serializers.CharField()


class ChangeNumberOfPhoneSerializer(serializers.Serializer):
    number_of_phone = serializers.CharField()


class ChangeTagsOfUserSerializer(serializers.Serializer):
    tags_of_user = serializers.CharField()


class SuccessChangeSerializer(serializers.Serializer):
    response = serializers.IntegerField(default=200)


class UnSuccessChangeSerializer(serializers.Serializer):
    response = serializers.CharField()