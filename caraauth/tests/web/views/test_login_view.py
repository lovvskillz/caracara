from time import time

from django.contrib.auth import get_user_model
from django_otp.oath import TOTP
from pytest import fixture, mark
from rest_framework import status
from rest_framework.reverse import reverse

LOGIN_URL = reverse("web:auth:login")
user_data = {
    "username": "username123",
    "email": "user@example.com",
    "password": "password123",
}


@fixture
def user():
    return get_user_model().objects.create_user(**user_data)


@fixture
def user_2fa(user):
    user.get_or_create_totp_device(confirmed=True)
    return user


def test__login_page(webtest):
    """
    Ensure that the login page is available.
    """
    login_page = webtest().get(LOGIN_URL)

    assert login_page.status_code == status.HTTP_200_OK


@mark.parametrize("username_or_email", [user_data["username"], user_data["email"]])
@mark.django_db
def test__with_valid_data(webtest, user, username_or_email, web_client):
    """
    Ensure that login works with valid user data.
    """
    login_page = webtest().get(LOGIN_URL)
    login_form = login_page.form
    login_form["username"] = username_or_email
    login_form["password"] = user_data["password"]

    response = login_form.submit()

    assert response.url == reverse("web:user_area:dashboard")
    assert response.status_code == status.HTTP_302_FOUND


@mark.parametrize(
    "username_or_email, password",
    [
        ("user_not_found", "s0me-password"),
        (user_data.get("username"), "password-1s-wrong"),
        (user_data.get("email"), "password-1s-wrong"),
    ],
)
@mark.django_db
def test__with_invalid_data(webtest, user, username_or_email, password):
    """
    Ensure user can't log in with invalid data.
    """
    login_page = webtest().get(LOGIN_URL)
    login_form = login_page.form
    login_form["username"] = username_or_email
    login_form["password"] = password

    response = login_form.submit()

    assert response.status_code == status.HTTP_200_OK
    assert (
        "No account was found with this username / email address and password!"
        in response.body.decode()
    )


@mark.django_db
def test__2fa_enabled(user_2fa, webtest):
    """
    Log in user with 2FA enabled if otp token is valid.
    """
    device = user_2fa.get_or_create_totp_device()
    totp = TOTP(device.bin_key, device.step, device.t0, device.digits, device.drift)
    totp.time = time()
    login_page = webtest().get(LOGIN_URL)
    login_form = login_page.form
    login_form["username"] = user_data["username"]
    login_form["password"] = user_data["password"]
    login_form["otp"] = str(totp.token()).rjust(6, "0")

    response = login_form.submit()

    assert response.url == reverse("web:user_area:dashboard")
    assert response.status_code == status.HTTP_302_FOUND


@mark.parametrize(
    "otp, error_message",
    [
        ("", "Token is not valid"),
        ("000000", "Token is not valid"),
        (
            "clearly invalid token",
            "The token length needs to be 6 or 8 characters long.",
        ),
    ],
)
@mark.django_db
def test__2fa_enabled__invalid_token(user_2fa, webtest, web_client, otp, error_message):
    """
    Deny login with invalid otp token.
    """
    login_page = webtest().get(LOGIN_URL)
    login_form = login_page.form
    login_form["username"] = user_data["username"]
    login_form["password"] = user_data["password"]
    login_form["otp"] = otp

    response = login_form.submit()

    assert response.status_code == status.HTTP_200_OK
    assert error_message in response.form.text
