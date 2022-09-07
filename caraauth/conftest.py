from _pytest.fixtures import fixture
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'caraauth.User'

    username = 'some_user'
    is_superuser = False


@fixture
def admin_user():
    return UserFactory.create(is_superuser=True)
