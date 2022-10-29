from time import time

from django.contrib.auth import get_user_model
from django_otp.oath import TOTP
from durin.models import AuthToken
from pytest import fixture, mark
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse

LOGIN_URL = reverse('auth_api:login')
user_data = {
    'username': 'username123',
    'email': 'user@example.com',
    'password': 'password123',
}


@fixture
def user():
    return get_user_model().objects.create_user(**user_data)


@fixture
def user_2fa(user):
    user.get_or_create_totp_device(confirmed=True)
    return user


@mark.parametrize('username_or_email', [user_data['username'], user_data['email']])
@mark.django_db
def test__with_valid_data(apitest, user, username_or_email, web_client):
    """
    Ensure that login works with valid user data.
    """
    data = {'username': username_or_email, 'password': user_data['password']}

    response = apitest().post(LOGIN_URL, data=data)
    token = AuthToken.objects.get(user=user, client=web_client)

    assert response.status_code == status.HTTP_200_OK
    assert 'expiry' in response.data
    assert response.data['token'] == token.token


@mark.parametrize(
    'username_or_email, password',
    [
        ('user_not_found', 's0me-password'),
        (user_data.get('username'), 'password-1s-wrong'),
        (user_data.get('email'), 'password-1s-wrong'),
    ],
)
@mark.django_db
def test__with_invalid_data(apitest, user, username_or_email, password):
    """
    Ensure user can't log in with invalid data.
    """
    data = {'username': username_or_email, 'password': password}

    response = apitest().post(LOGIN_URL, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        'non_field_errors': [
            ErrorDetail(
                string=(
                    "No account was found with this username / email address and"
                    " password!"
                ),
                code='authorization',
            )
        ]
    }


@mark.django_db
def test__2fa_enabled(user_2fa, apitest, web_client):
    """
    Log in user with 2FA enabled if otp token is valid.
    """
    device = user_2fa.get_or_create_totp_device()
    totp = TOTP(device.bin_key, device.step, device.t0, device.digits, device.drift)
    totp.time = time()
    data = {
        'username': user_data['username'],
        'password': user_data['password'],
        'otp': str(totp.token()).rjust(6, '0'),
    }

    response = apitest().post(LOGIN_URL, data=data)
    token = AuthToken.objects.get(user=user_2fa, client=web_client)

    assert response.status_code == status.HTTP_200_OK
    assert 'expiry' in response.data
    assert response.data['token'] == token.token


@mark.parametrize(
    'otp, error_message',
    [
        ('', "Token is not valid"),
        ('000000', "Token is not valid"),
        (
            'clearly invalid token',
            "The token length needs to be 6 or 8 characters long.",
        ),
    ],
)
@mark.django_db
def test__2fa_enabled__invalid_token(user_2fa, apitest, web_client, otp, error_message):
    """
    Deny login with invalid otp token.
    """
    data = {
        'username': user_data['username'],
        'password': user_data['password'],
        'otp': otp,
    }

    response = apitest().post(LOGIN_URL, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data['otp'][0]) == error_message
