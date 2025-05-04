from rest_framework import serializers


class NewAccountData(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.IntegerField()
    pow = serializers.IntegerField()
    nickname = serializers.CharField()


class ResponseOf400FromCreateNewAccount(serializers.Serializer):
    error_code = serializers.IntegerField(default=1)
    message = serializers.CharField(default='Не найдено значение pow в запросе либо не найден куки файл.')


class ResponseOf409FromCreateNewAccount(serializers.Serializer):
    error_code = serializers.IntegerField(default=2)
    message = serializers.CharField(default='Данный логин уже занят.')


class ResponseOf401FromCreateNewAccount(serializers.Serializer):
    error_code = serializers.IntegerField(default=3)
    message = serializers.CharField(default='Недействительный куки.')


class ChallengeData(serializers.Serializer):
    random_string = serializers.CharField()
    timestamp = serializers.IntegerField()
    count_of_bits = serializers.IntegerField(default=3)
    version = serializers.IntegerField(default=1)
    resource = serializers.CharField(default='pollster')
    extension = serializers.CharField()