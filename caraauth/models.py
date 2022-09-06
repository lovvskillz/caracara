from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from caraauth.validators import UsernameValidator


class User(AbstractUser):
    """
    Custom User model. Includes default Django fields and can be easily extended.
    """

    username_validator = UsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=64,
        unique=True,
        help_text=_("Required. 5 - 64 characters. Letters, digits and _ only."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
