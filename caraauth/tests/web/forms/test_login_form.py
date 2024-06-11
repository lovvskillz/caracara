from django.core.exceptions import NON_FIELD_ERRORS
from pytest import mark

from caraauth.forms import RegisterForm, LoginForm
from caraauth.tests.factories import UserFactory


@mark.django_db
@mark.parametrize('username_or_email', ['not-found', 'not-found@example.com'])
def test__username_or_email_not_found(user, username_or_email):
    """
    Ensure that an error is raised if the user was not found.
    """
    UserFactory.create(username="some-user", password="strong-password123")

    form = LoginForm(
        data={
            'username_or_email': username_or_email,
            'password': 'strong-password123',
        }
    )

    assert not form.is_valid()
    assert form.errors == {NON_FIELD_ERRORS: ["No account was found with this username / email address and password!"]}


@mark.django_db
def test__valid():
    """
    Ensure that a valid user information don't raise an error.
    """
    UserFactory(username="g4m3r", password="strong-password123")

    form = LoginForm(
        data={
            'username_or_email': "g4m3r",
            'password': 'strong-password123',
        }
    )

    assert form.is_valid()
