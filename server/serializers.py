from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from server.models import UserGameServer

PERIOD_CHOICES = [
    (1, _("1 day")),
    (3, _("3 days")),
    (7, _("7 days")),
    (10, _("10 days")),
    (14, _("14 days")),
    (30, _("30 days")),
    (60, _("60 days")),
    (90, _("90 days")),
]


class CreateServerSerializer(serializers.ModelSerializer):
    with_own_ip = serializers.BooleanField(label=_("With own IP address"))
    period = serializers.IntegerField(choices=PERIOD_CHOICES, label=_("Rental period"))

    class Meta:
        model = UserGameServer
        fields = ['server_name', 'ram', 'disk_space', 'cores', 'with_own_ip', 'period']
