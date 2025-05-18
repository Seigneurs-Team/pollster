from rest_framework import serializers

from Configs.Serializers.main_page import ListOfPolls


class SuccessResponseOnGetAdminPanel(serializers.Serializer):
    all_objects = serializers.ListField(child=ListOfPolls())