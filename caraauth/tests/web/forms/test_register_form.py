from django.utils.crypto import get_random_string
from pytest import mark
from rest_framework.exceptions import ErrorDetail

from caraauth.forms import RegisterForm


@mark.django_db
@mark.parametrize(
    'username_length, error',
    [
        (
            4,
            "Ensure this value has at least 5 characters (it has 4).",
        ),
        (
            65,
            "Ensure this value has at most 64 characters (it has 65).",
        ),
    ],
)
def test__username_length_out_of_range(username_length, error):
    """
    Ensure that a username needs to contain between 5 and 64 chars.
    """
    username = get_random_string(username_length)
    form = RegisterForm(
        data={
            'username': username,
            'email': 'generic.mail@example.com',
            'password': 'strong-password123',
        }
    )
    assert not form.is_valid()
    assert form.errors == {'username': [error]}


@mark.django_db
@mark.parametrize(
    'invalid_username', ('my@name', 'my.name', 'hello-world', '§$6350ß$§%§"$)()$§=_')
)
def test__username_contains_invalid_chars(invalid_username):
    """
    Ensure that a username can only contain letters, numbers and _ chars.
    """
    form = RegisterForm(
        data={
            'username': invalid_username,
            'email': 'generic.mail@example.com',
            'password': 'strong-password123',
        }
    )
    assert not form.is_valid()
    assert form.errors == {
        'username': [
            "Enter a valid username. This value may contain only letters,"
            " numbers, _ characters and should be at least 5 characters long."
        ]
    }


@mark.django_db
@mark.parametrize('valid_username', ('my_name', 'myname', 'g4m3r_123_HD'))
def test__valid_username(valid_username):
    """
    Ensure that valid username don't raise an error.
    """
    form = RegisterForm(
        data={
            'username': valid_username,
            'email': 'generic.mail@example.com',
            'password': 'strong-password123',
        }
    )
    assert form.is_valid()
