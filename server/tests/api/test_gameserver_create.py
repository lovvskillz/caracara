from datetime import timedelta

import freezegun
from django.utils import timezone
from pytest import mark
from rest_framework import status
from rest_framework.reverse import reverse

from server.models import GameSoftwareVersion, Node, UserGameServer

URL = reverse('api:server:gameserver-list')


@mark.django_db
@freezegun.freeze_time('01-01-2023')
def test__create_gameserver__valid(apitest, user, basic_server_setup):
    """
    Ensure that a gameserver can be created.
    """
    server_name = 'CaraCaraCraft'
    ram = 1024
    disk_space = 1024
    cores = 2
    period = 30
    with_own_ip = True
    software_version = GameSoftwareVersion.objects.get()

    response = apitest(user).post(
        URL,
        {
            'server_name': server_name,
            'ram': ram,
            'disk_space': disk_space,
            'cores': cores,
            'period': period,
            'with_own_ip': with_own_ip,
            'software_version': software_version.id,
        },
    )
    gameserver = UserGameServer.objects.get()

    assert response.status_code == status.HTTP_201_CREATED
    assert gameserver.server_name == server_name
    assert gameserver.ram == ram
    assert gameserver.disk_space == disk_space
    assert gameserver.cores == cores
    assert gameserver.available_until == timezone.now() + timedelta(days=period)
    assert gameserver.own_ip
    assert gameserver.software_version == software_version
    assert gameserver.node == Node.objects.get()
