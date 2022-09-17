from factory.django import DjangoModelFactory
from pytest import fixture
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from caraauth.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'caraauth.User'

    username = 'some_user'
    is_superuser = False
    is_active = True


@fixture
def user() -> User:
    return UserFactory.create()


@fixture
def admin_user() -> User:
    return UserFactory.create(is_superuser=True)


@fixture
def apitest():
    """
    Return API client.
    """

    def _auth(user: User = None) -> APIClient:
        """
        Return API client with optional authorization header if user is set.
        """
        api_client = APIClient()
        if user:
            token = RefreshToken.for_user(user)
            api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        return api_client

    return _auth
