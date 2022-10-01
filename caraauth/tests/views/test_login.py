from django.contrib.auth import get_user_model
from durin.models import AuthToken
from pytest import fixture, mark
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse

LOGIN_URL = reverse('auth:login')
user_data = {
    'username': 'username123',
    'email': 'user@example.com',
    'password': 'password123',
}


@fixture
def user():
    return get_user_model().objects.create_user(**user_data)


@mark.parametrize(
    'username_or_email', [user_data.get('username'), user_data.get('email')]
)
@mark.django_db
def test__with_valid_data(apitest, user, username_or_email, web_client):
    """
    Ensure that login works with valid user data.
    """
    data = {'username': username_or_email, 'password': user_data.get('password')}

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
