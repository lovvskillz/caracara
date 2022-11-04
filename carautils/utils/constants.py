from datetime import datetime

from django.utils import timezone

POSIX_ZERO = timezone.make_aware(datetime(1970, 1, 1))
