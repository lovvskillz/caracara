from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from caraauth.serializers import UserProfileSerializer


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        user_data = self.serializer_class(instance=request.user)
        return Response(data=user_data.data)

    def post(self, request, *args, **kwargs):
        user_data = self.serializer_class(instance=request.user, data=request.data)
        if user_data.is_valid(raise_exception=True):
            user_data.save()
        return Response(data=user_data.data)
