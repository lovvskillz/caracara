from _pytest.fixtures import fixture
from factory.django import DjangoModelFactory


@fixture
def webtest(client):
    return client


class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'caraauth.User'

    username = 'some_user'
    is_superuser = False
    is_active = True


@fixture
def user():
    return UserFactory.create()


@fixture
def admin_user():
    return UserFactory.create(is_superuser=True)
