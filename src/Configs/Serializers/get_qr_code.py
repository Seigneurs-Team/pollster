from rest_framework import serializers


class QrCode(serializers.Serializer):
    qr_code = serializers.CharField()
    url_on_poll = serializers.CharField()


class SuccessResponseOfGetQRCode(QrCode):
    pass