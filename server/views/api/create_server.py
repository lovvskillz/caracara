from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class CreateGameserver(APIView):
    permission_classes = (IsAuthenticated,)
