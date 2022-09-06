from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r"^[\w]{5,}\Z"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, _ characters and should be at least 5 characters long."
    )
    flags = 0
