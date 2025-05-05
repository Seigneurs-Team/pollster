from rest_framework import serializers


class SuccessResponseOfGetQRCode(serializers.Serializer):
    qr_code = serializers.CharField()
    url_on_poll = serializers.CharField()