from base64 import b32encode

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from caraauth.authentication import Has2FADisabled, Has2FAEnabled
from caraauth.serializers import (
    ConfirmTOTPDeviceSerializer,
    OTPSerializer,
    StaticTokenSerializer,
)


class Setup2FAView(APIView):
    permission_classes = (Has2FADisabled,)

    def get(self, request, *args, **kwargs):
        device = request.user.enable_2fa()
        data = {
            "totp_secret": b32encode(device.bin_key).decode(),
            "config_url": device.config_url,
        }
        return Response(data=data)

    def post(self, request, *args, **kwargs):
        otp_serializer = ConfirmTOTPDeviceSerializer(
            data=request.data, user=request.user
        )
        otp_serializer.is_valid(raise_exception=True)
        tokens = request.user.create_static_device()
        static_token_serializer = StaticTokenSerializer(tokens, many=True)
        return Response(data={"static_tokens": static_token_serializer.data})


class BackupTokensView(APIView):
    permission_classes = (Has2FAEnabled,)

    def get(self, request, *args, **kwargs):
        tokens = request.user.static_device_tokens
        static_token_serializer = StaticTokenSerializer(tokens, many=True)
        return Response(data={"static_tokens": static_token_serializer.data})


class RefreshBackupTokensView(APIView):
    permission_classes = (Has2FAEnabled,)

    def post(self, request, *args, **kwargs):
        tokens = request.user.refresh_static_device_tokens()
        static_token_serializer = StaticTokenSerializer(tokens, many=True)
        return Response(data={"static_tokens": static_token_serializer.data})


class Disable2FAView(APIView):
    permission_classes = (Has2FAEnabled,)

    def post(self, request, *args, **kwargs):
        otp_serializer = OTPSerializer(data=request.data)
        otp_serializer.is_valid(raise_exception=True)
        otp = otp_serializer.validated_data.get("otp")
        if request.user.confirm_any_device_by_otp(otp):
            request.user.disable_2fa()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
