from django.contrib.auth import get_user_model
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from caraauth.serializers import UserProfileSerializer


class SettingsViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    queryset = get_user_model().objects.all()
