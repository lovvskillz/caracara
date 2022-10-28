from django.db.models import Manager, Q, QuerySet
from django.utils import timezone

from utils.constants import POSIX_ZERO


class BaseQuerySet(QuerySet):
    ...


class BaseManager(Manager):
    ...


class SoftDeleteQuerySet(BaseQuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # default filter, must be applied always
        self.query.add_q(Q(deleted_at=POSIX_ZERO))

    def delete(self):
        """
        customized version of delete that does only soft-delete
        """
        now = timezone.now()
        return super().update(deleted_at=now, modified_at=now)


class SoftDeleteManager(Manager):
    """
    custom manager class ...does nothing special for now
    """

    def get_queryset(self):
        """
        Returns a new QuerySet object
        """
        return SoftDeleteQuerySet(self.model, using=self._db)
