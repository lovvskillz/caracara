from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from utils.db.models import BaseModel


class Node(BaseModel):
    ip = models.CharField(_("IP"), max_length=15)
    cores = models.PositiveIntegerField(_("Cores"))
    ram = models.PositiveIntegerField(_("RAM (MB)"))
    disk_space = models.PositiveIntegerField(_("Disk Space (GB)"))

    def __str__(self):
        return f"{self.ip}"


class Game(BaseModel):
    title = models.CharField(_("Name"), max_length=64)
    slug = models.CharField(_("URL"), max_length=256, blank=True, unique=True)
    min_ram = models.PositiveIntegerField(_("Minimum RAM (MB)"))
    min_disk_space = models.PositiveIntegerField(_("Minimum Disk Space (MB)"))

    class Meta:
        verbose_name = _("Game")
        verbose_name_plural = _("Games")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title.lower())
        super().save(*args, **kwargs)


class GameSoftware(BaseModel):
    game = models.ForeignKey('Game', on_delete=models.CASCADE, verbose_name=_("Game"))
    name = models.CharField(_("Software Name"), max_length=64)
    name_suffix = models.CharField(
        _("Software Name Suffix"), max_length=64, blank=True, default=""
    )
    default_port = models.PositiveIntegerField(_("Default Port"))

    class Meta:
        verbose_name = _("Game Software")
        verbose_name_plural = _("Game Software")

    def __str__(self):
        name = f"{self.name}"
        if self.name_suffix:
            name = f"{name} {self.name_suffix}"
        return name


class GameSoftwareVersion(BaseModel):
    software = models.ForeignKey(
        'GameSoftware', on_delete=models.CASCADE, verbose_name=_("Game Software")
    )
    version = models.CharField(_("Software Version"), max_length=64)
    version_suffix = models.CharField(
        _("Software Version Suffix"), max_length=64, blank=True, default=""
    )

    class Meta:
        verbose_name = _("Software Version")
        verbose_name_plural = _("Software Versions")
