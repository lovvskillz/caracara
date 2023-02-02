from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from carautils import constants
from carautils.utils.date import add_days_to_now
from carautils.utils.server import (
    get_available_own_ip,
    get_available_port,
    get_node_for_hosting,
)
from server.models import UserGameServer
from server.views.exceptions import GameserverError

if TYPE_CHECKING:
    from server.models import GameSoftwareVersion, Node


class GameserverSerializer(serializers.ModelSerializer):
    disk_space = serializers.ChoiceField(
        choices=constants.DISK_SPACE_CHOICES,
        label=_("Select disk space"),
    )
    period = serializers.ChoiceField(
        choices=constants.PERIOD_CHOICES,
        label=_("Select rental period"),
        write_only=True,
    )
    ram = serializers.ChoiceField(choices=constants.RAM_CHOICES, label=_("Select RAM"))
    with_own_ip = serializers.BooleanField(
        label=_("With own IP address"), write_only=True
    )

    class Meta:
        model = UserGameServer
        fields = [
            'server_name',
            'software_version',
            'ram',
            'disk_space',
            'cores',
            'period',
            'with_own_ip',
        ]

    def save(self, **kwargs):
        """Remove none-model fields before saving data"""
        self._validated_data.pop('period')
        self._validated_data.pop('with_own_ip')
        return super().save(**kwargs)

    def validate(self, attrs):
        node = self._validate_available_space(attrs.get('ram'), attrs.get('disk_space'))
        own_ip = self._get_own_ip() if attrs.get('with_own_ip') else None
        port = self._get_port(node, attrs.get('software_version'))
        attrs.update(
            {
                'node': node,
                'own_ip': own_ip,
                'port': port,
                'available_until': add_days_to_now(attrs.get('period')),
            }
        )
        return attrs

    def _validate_available_space(self, ram: int, disk_space: int) -> 'Node':
        if node := get_node_for_hosting(ram, disk_space):
            return node
        raise GameserverError(
            detail=_("There is not enough free space for this configuration.")
        )

    def _get_own_ip(self) -> str:
        if own_ip := get_available_own_ip():
            return own_ip
        raise GameserverError(detail=_("There is no available IP addresses left."))

    def _get_port(self, node: 'Node', software_version: 'GameSoftwareVersion') -> int:
        if port := get_available_port(node, software_version.software.default_port):
            return port
        raise GameserverError(detail=_("There is no available IP addresses left."))
