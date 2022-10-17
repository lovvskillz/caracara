from time import time

from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice
from pytest import mark
from rest_framework import status
from rest_framework.reverse import reverse

setup_2fa_url = reverse('user_area:setup_2fa')


@mark.django_db
def test__setup_2fa__success(user, apitest):
    # setup totp device
    response = apitest(user).get(setup_2fa_url)
    assert response.status_code == status.HTTP_200_OK
    assert 'totp_secret' in response.data
    assert 'config_url' in response.data

    # generate token
    totp_device = TOTPDevice.objects.first()
    totp = TOTP(totp_device.bin_key)
    totp.time = time()
    token = totp.token()

    # confirm 2fa setup
    response = apitest(user).post(setup_2fa_url, data={'otp': token})
    assert response.status_code == status.HTTP_200_OK
    assert user.has_2fa_enabled


@mark.django_db
def test__setup_2fa__already_enabled(user_2fa, apitest):
    """
    Refuse 2FA setup for users with enabled 2fa.
    """
    response = apitest(user_2fa).get(setup_2fa_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
