from rest_framework import serializers


class NewAccountData(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.IntegerField()
    pow = serializers.IntegerField()
    nickname = serializers.CharField()