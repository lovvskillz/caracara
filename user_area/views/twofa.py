from base64 import b32encode

from rest_framework.response import Response
from rest_framework.views import APIView

from caraauth.authentication import Has2FADisabled
from caraauth.serializers import ConfirmTOTPDeviceSerializer


class Setup2FAView(APIView):
    permission_classes = (Has2FADisabled,)

    def get(self, request, *args, **kwargs):
        device = request.user.get_or_create_totp_device()
        data = {
            'totp_secret': b32encode(device.bin_key).decode(),
            'config_url': device.config_url,
        }
        return Response(data=data)

    def post(self, request, *args, **kwargs):
        otp_serializer = ConfirmTOTPDeviceSerializer(
            data=request.data, user=request.user
        )
        otp_serializer.is_valid(raise_exception=True)
        tokens = request.user.create_static_device()
        return Response(data={'static_tokens': tokens})
