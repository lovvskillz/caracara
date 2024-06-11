from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from django_otp import user_has_device

from caraauth import validators
from caraauth.utils import two_fa
from carautils.utils.db.models import BaseModel

if TYPE_CHECKING:
    from django_otp.plugins.otp_totp.models import TOTPDevice


class User(AbstractUser, BaseModel):
    """
    Custom User model. Includes default Django fields and can be easily extended.
    """

    username_validator = validators.UsernameValidator()
    password_validator = validators.PasswordValidator()

    username = models.CharField(
        _("username"),
        max_length=64,
        unique=True,
        help_text=_("Required. 5 - 64 characters. Letters, digits and _ only."),
        validators=[MinLengthValidator(limit_value=5), username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), unique=True)
    password = models.CharField(
        _("password"),
        max_length=128,
        help_text=_(
            "Required. Need to have at least 8 characters containing letters and "
            "digits."
        ),
        validators=[password_validator],
    )
    last_login = models.DateTimeField(_("Last Login"), default=timezone.now)

    def get_profile_as_dict(self):
        """
        Return user instance as serialized data.
        """
        return import_string(settings.USER_SERIALIZER)(instance=self).data

    @property
    def has_2fa_enabled(self):
        return user_has_device(self)

    def enable_2fa(self):
        return self.get_or_create_totp_device()

    def disable_2fa(self):
        return two_fa.delete_devices_for_user(self)

    def get_or_create_totp_device(self, confirmed: bool = False) -> "TOTPDevice":
        """
        Return existing TOTP Device or create new one.
        """
        if not (device := two_fa.get_user_totp_device(self)):
            device = self.totpdevice_set.create(confirmed=confirmed, name="default")
        return device

    def create_static_device(self):
        """
        Create a user's static device.
        """
        return two_fa.create_static_device(self)

    @property
    def static_device_tokens(self):
        """
        Get user's static device tokens.
        """
        return two_fa.get_static_device_tokens(self)

    def refresh_static_device_tokens(self):
        """
        Replace current static device tokens with new ones.
        """
        if device := two_fa.get_user_static_device(self):
            return two_fa.generate_static_device_tokens(self, device)
        return []

    def verify_totp_device(self, otp: str) -> bool:
        """
        Verify user's default TOTP device.
        """
        return two_fa.verify_totp_device(self, otp)

    def confirm_any_device_by_otp(self, otp: str) -> bool:
        """
        Confirm that provided otp is valid a user's TOTP or static device.
        """
        return two_fa.confirm_any_device_token(self, otp)

    def update_last_login(self):
        """
        Update last login to current timestamp.
        """
        self.last_login = timezone.now()
