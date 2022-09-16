from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r"^[\w]+\Z"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, _ characters and should be at least 5 characters long."
    )
    flags = 0


@deconstructible
class PasswordValidator(validators.RegexValidator):
    regex = r"^(?=.*[\d])(?=.*[\w]).{8,}\Z"
    message = _(
        "Enter a valid password. Should be at least 8 characters long containing"
        " letters and numbers."
    )
    flags = 0
