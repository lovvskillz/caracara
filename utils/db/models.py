from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.constants import POSIX_ZERO
from utils.db.managers import BaseManager, SoftDeleteManager


class BaseModel(models.Model):
    """
    Add fields that should be available in every model.
    """

    created_at = models.DateTimeField(
        default=timezone.now, blank=True, verbose_name=_("Created at")
    )
    modified_at = models.DateTimeField(
        default=POSIX_ZERO, blank=True, verbose_name=_("Modified at")
    )
    objects = BaseManager()

    class Meta:
        abstract = True
        ordering = ('created_at', 'id')


class SoftDeleteModel(BaseModel):
    """
    Add soft delete functionality to a model.
    """

    deleted_at = models.DateTimeField(
        default=POSIX_ZERO, blank=True, verbose_name=_('Deleted at')
    )
    objects = SoftDeleteManager()

    class Meta:
        abstract = True
        ordering = ('created_at', 'id')

    def save(self, *args, **kwargs):
        self.modified_at = timezone.now()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        now = timezone.now()
        self.deleted_at = now
        self.modified_at = now
        self.save(update_fields=['deleted_at', 'modified_at'])
