from datetime import timedelta
from typing import TYPE_CHECKING

from django.utils import timezone

if TYPE_CHECKING:
    from datetime import datetime


def add_days_to_now(days: int = 0) -> 'datetime':
    """
    Append days to current datetime.
    """
    return timezone.now() + timedelta(days=days)
