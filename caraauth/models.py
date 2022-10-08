from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from django_otp import user_has_device

from caraauth import validators
from caraauth.utils.two_fa import get_user_totp_device

if TYPE_CHECKING:
    from django_otp.plugins.otp_totp.models import TOTPDevice


class User(AbstractUser):
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
    email = models.EmailField(_("email address"))
    password = models.CharField(
        _("password"),
        max_length=128,
        help_text=_(
            "Required. Need to have at least 8 characters containing letters and "
            "digits."
        ),
        validators=[password_validator],
    )

    @property
    def has_2fa_enabled(self):
        return user_has_device(self)

    def get_or_create_totp_device(self, confirmed: bool = False) -> 'TOTPDevice':
        """
        Return existing TOTP Device or create new one.
        """
        if not (device := get_user_totp_device(self)):
            device = self.totpdevice_set.create(confirmed=confirmed, name='default')
        return device

    def get_profile_as_dict(self):
        """
        Return user instance as serialized data.
        """
        return import_string(settings.USER_SERIALIZER)(instance=self).data
