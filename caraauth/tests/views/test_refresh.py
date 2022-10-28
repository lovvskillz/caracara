from django.utils import timezone
from durin.models import AuthToken
from freezegun import freeze_time
from pytest import mark
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.fields import DateTimeField
from rest_framework.reverse import reverse

REFRESH_URL = reverse('auth_api:refresh')


@freeze_time('2022-09-01')
@mark.django_db
def test_refresh_token(apitest, user, web_client):
    """
    Ensure that users with valid refresh token can obtain a new access token.
    """
    expiry = timezone.now() + web_client.token_ttl
    new_expired_datetime = DateTimeField().to_representation(expiry)

    response = apitest(user).post(REFRESH_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['expiry'] == new_expired_datetime


@mark.django_db
def test_refresh_token__not_authenticated(apitest):
    """
    Ensure that users need to be authenticated to refresh token.
    """
    response = apitest().post(REFRESH_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.django_db
def test_refresh_token__is_invalid(apitest, user):
    """
    Ensure that an invalid token will not return an access token.
    """
    apitest = apitest(user)
    apitest._credentials['HTTP_AUTHORIZATION'] = 'Bearer invalidtoken123'
    response = apitest.post(REFRESH_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {
        'detail': ErrorDetail(string="Invalid token.", code='authentication_failed')
    }


@mark.django_db
def test_refresh_token__is_expired(apitest, user, web_client):
    """
    Ensure that an expired refresh token will not return an access token.
    """
    with freeze_time('2022-09-01'):
        AuthToken.objects.create(user=user, client=web_client)

    with freeze_time('2022-09-30'):  # refresh token should be invalid
        response = apitest(user).post(REFRESH_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {
        'detail': ErrorDetail(
            string="The given token has expired.", code='authentication_failed'
        )
    }
