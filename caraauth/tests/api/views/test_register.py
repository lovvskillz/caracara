from django.contrib.auth import get_user_model
from pytest import mark
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse

from conftest import UserFactory

REGISTER_URL = reverse('auth_api:register')
VALID_USER_DATA = {
    'username': 'new_user',
    'email': 'new.user@example.com',
    'password': 'some-safe-password-123',
}


@mark.django_db
def test_user_data_is_valid(apitest):
    """
    Ensure that a new user can be created with valid data.
    """
    assert get_user_model().objects.count() == 0
    response = apitest().post(REGISTER_URL, data=VALID_USER_DATA)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['user'] == {
        'email': 'new.user@example.com',
        'username': 'new_user',
    }
    assert 'token' in response.data
    assert 'expiry' in response.data
    assert get_user_model().objects.count() == 1


@mark.django_db
def test__no_data_submitted(apitest):
    """
    Don't create a user if no data is submitted.
    """
    response = apitest().post(REGISTER_URL, data={})

    assert get_user_model().objects.count() == 0
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        'email': [ErrorDetail(string="This field is required.", code='required')],
        'username': [ErrorDetail(string="This field is required.", code='required')],
        'password': [ErrorDetail(string="This field is required.", code='required')],
    }


@mark.django_db
def test__invalid_field_data(apitest):
    """
    Don't create a user with invalid data on any field.
    """
    invalid_data = {
        'username': 'new_user@-./',
        'email': 'invalid.mail.com',
        'password': 'short',
    }

    response = apitest().post(REGISTER_URL, data=invalid_data)

    assert get_user_model().objects.count() == 0
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        'email': [ErrorDetail(string="Enter a valid email address.", code='invalid')],
        'username': [
            ErrorDetail(
                string=(
                    "Enter a valid username. This value may contain only letters,"
                    " numbers, _ characters and should be at least 5 characters long."
                ),
                code='invalid',
            )
        ],
        'password': [
            ErrorDetail(
                string=(
                    "Enter a valid password. Should be at least 8 characters long"
                    " containing letters and numbers."
                ),
                code='invalid',
            )
        ],
    }


@mark.parametrize(
    'username, email, duplicated_field, error',
    [
        (
            VALID_USER_DATA['username'],
            'another.mail@example.com',
            'username',
            "This username is already taken.",
        ),
        (
            VALID_USER_DATA['username'].upper(),
            'another.mail@example.com',
            'username',
            "This username is already taken.",
        ),
        (
            'just_a_username',
            VALID_USER_DATA['email'],
            'email',
            "This email address is already taken.",
        ),
        (
            'just_a_username',
            VALID_USER_DATA['email'].upper(),
            'email',
            "This email address is already taken.",
        ),
    ],
)
@mark.django_db
def test__duplicated_user_data(apitest, username, email, duplicated_field, error):
    """
    Ensure users with duplicated username or email can't be created.
    """
    UserFactory.create(
        username=username, email=email, password=VALID_USER_DATA['password']
    )

    response = apitest().post(REGISTER_URL, data=VALID_USER_DATA)

    assert get_user_model().objects.count() == 1
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        duplicated_field: [ErrorDetail(string=error, code='unique')]
    }
