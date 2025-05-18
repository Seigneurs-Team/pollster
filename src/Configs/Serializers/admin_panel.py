from rest_framework import serializers

from Configs.Serializers.main_page import Poll


class SuccessResponseOnGetAdminPanel(serializers.Serializer):
    all_objects = serializers.ListField(child=Poll())