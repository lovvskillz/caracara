from datetime import timedelta

from django_webtest import WebTest
from durin.models import AuthToken, Client
from factory import Sequence
from factory.django import DjangoModelFactory
from pytest import fixture
from pytest_factoryboy import register
from rest_framework.test import APIClient

from caraauth.models import User
from caraauth.tests.factories import UserFactory


@fixture
def user() -> User:
    return UserFactory.create()


@fixture
def user_2fa(user):
    user.get_or_create_totp_device(confirmed=True)
    user.create_static_device()
    return user


@fixture
def admin_user() -> User:
    return UserFactory.create(is_superuser=True)


@fixture
def web_client():
    """
    Return web client (durin) for api calls.
    """
    return Client.objects.get_or_create(name='web', token_ttl=timedelta(days=1))[0]


@fixture
def apitest(web_client):
    """
    Return API client to make requests.
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


@fixture
def webtest(django_app):
    """
    Return Web client to make requests.
    """

    def _auth(user: User = None) -> WebTest:
        """
        Return Web client with optional authorized user if set.
        """
        if user:
            django_app.set_user(user)
        return django_app

    return _auth
