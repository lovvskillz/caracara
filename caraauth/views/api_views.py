from typing import TYPE_CHECKING

from durin.models import AuthToken
from durin.views import RefreshView
from rest_framework.permissions import IsAuthenticated

from caraauth.mixins import AuthMixin
from caraauth.permissions import IsAnonymous
from caraauth.serializers import LoginSerializer, RegisterSerializer

if TYPE_CHECKING:
    from durin.models import Client


class RegisterView(AuthMixin):
    """
    Register a new user.
    """

    permission_classes = (IsAnonymous,)
    serializer_class = RegisterSerializer

    def get_token_obj(self, request, client: 'Client') -> 'AuthToken':
        return AuthToken.objects.create(request.user, client)


class LoginView(AuthMixin):
    """
    Authenticate a user.
    """

    permission_classes = (IsAnonymous,)
    serializer_class = LoginSerializer


class TokenRefreshView(RefreshView):
    """
    Refresh the token for the authenticated user.
    """

    permission_classes = (IsAuthenticated,)
