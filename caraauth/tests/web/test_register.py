from django.contrib.auth import get_user_model
from pytest import mark
from rest_framework import status
from rest_framework.reverse import reverse

from conftest import UserFactory

REGISTER_URL = reverse('auth_web:register')
VALID_USER_DATA = {
    'username': 'new_user',
    'email': 'new.user@example.com',
    'password': 'some-safe-password-123',
}


def test__register_page(webtest):
    """
    Ensure that the register page is available.
    """
    register_page = webtest().get(REGISTER_URL)

    assert register_page.status_code == status.HTTP_200_OK


@mark.django_db
def test__user_data_is_valid(webtest):
    """
    Ensure that a new user can be created with valid data.
    """
    assert get_user_model().objects.count() == 0
    register_page = webtest().get(REGISTER_URL)
    register_form = register_page.form
    register_form['username'] = VALID_USER_DATA['username']
    register_form['email'] = VALID_USER_DATA['email']
    register_form['password'] = VALID_USER_DATA['password']

    response = register_form.submit().follow()

    assert response.status_code == status.HTTP_200_OK
    assert get_user_model().objects.count() == 1


@mark.django_db
def test__no_data_submitted(webtest):
    """
    Don't create a user if no data is submitted.
    """
    register_page = webtest().get(REGISTER_URL)
    register_form = register_page.form

    response = register_form.submit()

    assert get_user_model().objects.count() == 0
    assert response.status_code == status.HTTP_200_OK
    assert "This field may not be blank." in response.form.text


@mark.django_db
def test__invalid_field_data(webtest):
    """
    Don't create a user with invalid data on any field.
    """
    register_page = webtest().get(REGISTER_URL)
    register_form = register_page.form
    register_form['username'] = 'new_user@-./'
    register_form['email'] = 'invalid.mail.com'
    register_form['password'] = 'short'

    response = register_form.submit()

    assert get_user_model().objects.count() == 0
    assert response.status_code == status.HTTP_200_OK
    assert "Enter a valid email address." in response.form.text
    assert (
        "Enter a valid username. This value may contain only letters,"
        " numbers, _ characters and should be at least 5 characters long."
        in response.form.text
    )
    assert (
        "Enter a valid password. Should be at least 8 characters long"
        " containing letters and numbers."
        in response.form.text
    )


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
def test__duplicated_user_data(webtest, username, email, duplicated_field, error):
    """
    Ensure users with duplicated username or email can't be created.
    """
    UserFactory.create(
        username=username, email=email, password=VALID_USER_DATA['password']
    )
    register_page = webtest().get(REGISTER_URL)
    register_form = register_page.form
    register_form['username'] = username
    register_form['email'] = email
    register_form['password'] = VALID_USER_DATA['password']

    response = register_form.submit()

    assert get_user_model().objects.count() == 1
    assert response.status_code == status.HTTP_200_OK
    assert error in response.form.text
