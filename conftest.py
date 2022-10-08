from datetime import timedelta

from durin.models import AuthToken, Client
from factory.django import DjangoModelFactory
from pytest import fixture
from rest_framework.test import APIClient

from caraauth.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'caraauth.User'

    username = 'some_user'
    email = 'some.user@example.com'
    is_superuser = False
    is_active = True


@fixture
def user() -> User:
    return UserFactory.create()


@fixture
def admin_user() -> User:
    return UserFactory.create(is_superuser=True)


@fixture
def web_client():
    return Client.objects.get_or_create(name='web', token_ttl=timedelta(days=1))[0]


@fixture
def apitest(web_client):
    """
    Return API client.
    """

    def _auth(user: User = None) -> APIClient:
        """
        Return API client with optional authorization header if user is set.
        """
        api_client = APIClient()
        headers = {'HTTP_X_API_CLIENT': web_client.name}
        if user:
            try:
                token = AuthToken.objects.get(user=user, client=web_client)
            except AuthToken.DoesNotExist:
                token = AuthToken.objects.create(user=user, client=web_client)
            headers['HTTP_AUTHORIZATION'] = f'Bearer {token.token}'
        api_client.credentials(**headers)
        return api_client

    return _auth
