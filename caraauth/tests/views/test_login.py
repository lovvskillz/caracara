from _pytest.fixtures import fixture
from django.contrib.auth import get_user_model
from pytest import mark
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
def test__with_valid_data(webtest, user, username_or_email):
    """
    Ensure that login works with valid user data.
    """
    data = {'username': username_or_email, 'password': user_data.get('password')}

    response = webtest.post(LOGIN_URL, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@mark.parametrize(
    'username_or_email, password',
    [
        ('user_not_found', 'some-password'),
        (user_data.get('username'), 'password-is-wrong'),
        (user_data.get('email'), 'password-is-wrong'),
    ],
)
@mark.django_db
def test__with_invalid_data(webtest, user, username_or_email, password):
    """
    Ensure user can't log in with invalid data.
    """
    data = {'username': username_or_email, 'password': password}

    response = webtest.post(LOGIN_URL, data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {
        'detail': ErrorDetail(
            string='No active account found with the given credentials',
            code='no_active_account',
        )
    }
