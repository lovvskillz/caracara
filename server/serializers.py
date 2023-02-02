from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from carautils import constants
from server.models import UserGameServer


class GameserverSerializer(serializers.ModelSerializer):
    disk_space = serializers.ChoiceField(
        choices=constants.DISK_SPACE_CHOICES,
        label=_("Select disk space"),
    )
    period = serializers.ChoiceField(
        choices=constants.PERIOD_CHOICES, label=_("Select rental period")
    )
    ram = serializers.ChoiceField(choices=constants.RAM_CHOICES, label=_("Select RAM"))
    with_own_ip = serializers.BooleanField(label=_("With own IP address"))

    class Meta:
        model = UserGameServer
        fields = ['server_name', 'ram', 'disk_space', 'cores', 'period', 'with_own_ip']
