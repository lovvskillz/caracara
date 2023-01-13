from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt

from carautils.utils.db.models import BaseModel, SoftDeleteModel
from server.manager import IPNetManager, UserGameserverManager
from server.validators import validate_cidr_notation

port_validator = MaxValueValidator(65535)

GAMESERVER_SETUP = 'setup'
GAMESERVER_ENABLED = 'enabled'
GAMESERVER_DELETE = 'delete'
GAMESERVER_DELETED = 'deleted'
GAMESERVER_DISABLED = 'disabled'
GAMESERVER_LOCKED = 'locked'
GAMESERVER_STATES = (
    (GAMESERVER_SETUP, _("is set up")),
    (GAMESERVER_ENABLED, _("enabled")),
    (GAMESERVER_DELETE, _("is being deleted")),
    (GAMESERVER_DELETED, _("deleted")),
    (GAMESERVER_DISABLED, _("disabled")),
    (GAMESERVER_LOCKED, _("locked")),
)


class Node(BaseModel):
    """
    The Node model describes a node used for game servers.
    """

    ip = models.GenericIPAddressField(_("IP Address"))
    cores = models.PositiveIntegerField(_("Cores"))
    ram = models.PositiveIntegerField(_("RAM (MB)"))
    disk_space = models.PositiveIntegerField(_("Disk Space (GB)"))

    def __str__(self):
        return f"{self.ip}"


class IPNet(BaseModel):
    """
    The IPNet Models defines an IP subnet.
    """

    ip_net = models.CharField(
        _("CIDR Notation"), max_length=18, validators=[validate_cidr_notation]
    )
    active = models.BooleanField(_("Active"), default=True)

    objects = IPNetManager()

    class Meta:
        verbose_name = _("IPNet")
        verbose_name_plural = _("IPNets")

    def split_cidr_notation(self):
        """
        Split the IP net and return net id and suffix as a tuple.
        """
        net_id, suffix = tuple(self.ip_net.split('/'))
        return net_id, int(suffix)

    @property
    def net_id(self):
        """
        Get the IP net id.
        """
        return self.split_cidr_notation()[0]

    @property
    def suffix(self):
        """
        Get the CIDR suffix.
        """
        return self.split_cidr_notation()[1]


class Game(BaseModel):
    """
    The Game models defines a game.
    """

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
    """
    The GameSoftware model defines a game software.
    """

    game = models.ForeignKey('Game', on_delete=models.CASCADE, verbose_name=_("Game"))
    name = models.CharField(_("Software Name"), max_length=64)
    name_suffix = models.CharField(
        _("Software Name Suffix"), max_length=64, blank=True, default=""
    )
    default_port = models.PositiveIntegerField(
        _("Default Port"), validators=[port_validator]
    )

    class Meta:
        verbose_name = _("Game Software")
        verbose_name_plural = _("Game Software")

    def __str__(self):
        name = f"{self.name}"
        if self.name_suffix:
            name = f"{name} {self.name_suffix}"
        return name


class GameSoftwareVersion(BaseModel):
    """
    The GameSoftwareVersion model defines a specific version of a game server software.
    """

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


class UserGameServer(SoftDeleteModel):
    """
    The UserGameServer model defines a user's game server.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )
    server_name = models.CharField(_("Gameserver Name"), max_length=64)
    software_version = models.ForeignKey(
        'GameSoftwareVersion',
        on_delete=models.PROTECT,
        verbose_name=_("Gameserver Software Version"),
    )
    node = models.ForeignKey(
        'Node', on_delete=models.PROTECT, verbose_name=_("Selected Node")
    )
    own_ip = models.GenericIPAddressField(
        _("Gameserver IP Address"), blank=True, null=True
    )
    port = models.PositiveIntegerField(
        _("Gameserver Port"), validators=[port_validator]
    )
    ram = models.PositiveIntegerField(_("Gameserver RAM"))
    disk_space = models.PositiveIntegerField(_("Gameserver Disk Space"))
    cores = models.PositiveIntegerField(_("Gameserver Cores"))
    available_until = models.DateTimeField(_("Available Until"))
    status = models.CharField(
        _("Gameserver Status"),
        choices=GAMESERVER_STATES,
        default=GAMESERVER_SETUP,
        max_length=64,
    )
    sql_password = encrypt(models.CharField(_("SQL Password"), max_length=64))
    ftp_password = encrypt(models.CharField(_("FTP Password"), max_length=64))
    extras = models.JSONField(_("Additional Data"), default=dict)

    objects = UserGameserverManager()

    class Meta:
        verbose_name = _("Gameserver")
        verbose_name_plural = _("Gameservers")

    def __str__(self):
        return f"{self.server_name} #{self.id}"

    @property
    def has_own_ip(self):
        return bool(self.own_ip)

    @property
    def ip(self):
        return self.own_ip if self.has_own_ip else self.node.ip
