from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from server.models import UserGameServer
from server.serializers import GameserverSerializer


class UserGameserverViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = GameserverSerializer

    def get_queryset(self):
        return UserGameServer.objects.from_user()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
