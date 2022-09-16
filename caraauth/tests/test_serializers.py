from django.utils.crypto import get_random_string
from pytest import mark
from rest_framework.exceptions import ErrorDetail

from caraauth.serializers import RegisterSerializer


@mark.django_db
@mark.parametrize(
    'username_length, error',
    [
        (
            4,
            ErrorDetail(
                string='Ensure this field has at least 5 characters.', code='min_length'
            ),
        ),
        (
            65,
            ErrorDetail(
                string='Ensure this field has no more than 64 characters.',
                code='max_length',
            ),
        ),
    ],
)
def test__register_serializer__username_length_out_of_range(username_length, error):
    """
    Ensure that a username needs to contain between 5 and 64 chars.
    """
    username = get_random_string(username_length)
    serializer = RegisterSerializer(
        data={
            'username': username,
            'email': 'generic.mail@example.com',
            'password': 'strong-password123',
        }
    )
    assert not serializer.is_valid()
    assert serializer.errors == {'username': [error]}


@mark.django_db
@mark.parametrize(
    'invalid_username', ('my@name', 'my.name', 'hello-world', '§$6350ß$§%§"$)()$§=_')
)
def test__register_serializer__username_contains_invalid_chars(invalid_username):
    """
    Ensure that a username can only contain letters, numbers and _ chars.
    """
    serializer = RegisterSerializer(
        data={
            'username': invalid_username,
            'email': 'generic.mail@example.com',
            'password': 'strong-password123',
        }
    )
    assert not serializer.is_valid()
    assert serializer.errors == {
        'username': [
            ErrorDetail(
                string=(
                    "Enter a valid username. This value may contain only letters,"
                    " numbers, _ characters and should be at least 5 characters long."
                ),
                code='invalid',
            )
        ]
    }


@mark.django_db
@mark.parametrize('valid_username', ('my_name', 'myname', 'g4m3r_123_HD'))
def test__register_serializer__valid_username(valid_username):
    """
    Ensure that valid username don't raise an error.
    """
    serializer = RegisterSerializer(
        data={
            'username': valid_username,
            'email': 'generic.mail@example.com',
            'password': 'strong-password123',
        }
    )
    assert serializer.is_valid()
