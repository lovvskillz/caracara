from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from caraauth.permissions import IsAnonymous
from caraauth.serializers import RegisterSerializer


class RegisterView(APIView):
    """
    Register a new user.
    """

    permission_classes = (IsAnonymous,)

    def post(self, request, *args, **kwargs) -> Response:
        register_serializer = RegisterSerializer(data=request.data)
        register_serializer.is_valid(raise_exception=True)
        token = TokenObtainPairSerializer(data=register_serializer.validated_data)
        token.is_valid(raise_exception=True)
        return Response(data={**register_serializer.data, **token.validated_data})


class LoginView(TokenObtainPairView):
    """
    Authenticate a user.
    """

    permission_classes = (IsAnonymous,)
