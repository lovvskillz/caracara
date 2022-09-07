from _pytest.fixtures import fixture


@fixture
def webtest(client):
    return client
