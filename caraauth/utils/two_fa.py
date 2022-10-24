from typing import Optional, TYPE_CHECKING, Union

from django.db.models import QuerySet
from django_otp import devices_for_user
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

if TYPE_CHECKING:
    from caraauth.models import User


def default_device(user: 'User') -> Union[Union['TOTPDevice', 'StaticToken'], bool]:
    """
    Return the user's default device.
    """
    if not user or user.is_anonymous:
        return False
    device = get_user_totp_device(user, True)
    if device is not None and device.name == 'default':
        return device
    return False


def get_user_totp_device(
    user: 'User', confirmed: Optional[bool] = None
) -> Optional['TOTPDevice']:
    """
    Return user's TOTP device.
    """
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device
    return None


def confirm_totp_device_token(user: 'User', token: str) -> bool:
    """
    Return weather the token is valid for a TOTP device.
    """
    device = get_user_totp_device(user, confirmed=True)
    if not device:
        return False
    verify_is_allowed = device.verify_is_allowed()[0]
    if not verify_is_allowed:
        return False
    if device.verify_token(token):
        return True
    return False


def verify_totp_device(user: 'User', token: str) -> bool:
    """
    Verify a TOTP device.
    """
    device = get_user_totp_device(user)
    if not device:
        return False
    verify_is_allowed, reason = device.verify_is_allowed()
    if not verify_is_allowed:
        return False
    if device.verify_token(token) and not device.confirmed:
        device.confirmed = True
        device.save()
        return True
    return False


def confirm_static_device_token(user: 'User', token: str) -> bool:
    """
    Return weather the token is valid for a static device.
    """
    device = get_user_static_device(user, True)
    if not device:
        return False
    verify_is_allowed, reason = device.verify_is_allowed()
    if not verify_is_allowed:
        return False
    if device.verify_token(token):
        return True
    return False


def get_user_static_device(
    user: 'User', confirmed: Optional[bool] = True
) -> Optional['StaticDevice']:
    """
    Return the first static device for a user.
    """
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, StaticDevice):
            return device
    return None


def create_static_device(user: 'User') -> 'QuerySet':
    """
    Create a static device and return 6 tokens.
    """
    device = get_user_static_device(user, True)
    if not device:
        device = StaticDevice.objects.create(user=user, name="Backup")
    return generate_static_device_tokens(device)


def generate_static_device_tokens(device: 'StaticDevice') -> 'QuerySet':
    """
    Generate new static device tokens for the given user.
    """
    device.token_set.all().delete()
    for n in range(6):
        token = StaticToken.random_token()
        device.token_set.create(token=token)
    return device.token_set.all()


def get_static_device_tokens(user: 'User') -> Union['QuerySet', list]:
    """
    Return tokens for a user's static device.
    """
    device = get_user_static_device(user, True)
    if device:
        return device.token_set.all()
    return []


def confirm_any_device_token(user: 'User', token: str) -> bool:
    """
    Return weather the token is valid for a TOTP or a static device.
    """
    if len(token) == 6:
        return confirm_totp_device_token(user, token)
    return confirm_static_device_token(user, token)
