from pytest import mark
from rest_framework import status
from rest_framework.reverse import reverse

URL = reverse("web:user_area:profile")


def test_permission__unauthenticated(webtest):
    """
    Ensure that unauthenticated users have no access to the profile page.
    """
    response = webtest().get(URL)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url.startswith(reverse("web:auth:login"))


@mark.django_db
def test_permission__authenticated(webtest, user):
    """
    Ensure that authenticated users can access the profile page
    """
    response = webtest(user).get(URL)

    assert response.status_code == status.HTTP_200_OK
