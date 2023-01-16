from pytest import mark

from carautils.utils.server import get_available_own_ip
from server.conftest import IPNetFactory, UserGameserverFactory
from server.models import IPNet, UserGameServer


@mark.django_db
def test_get_available_own_ip__first_available_ip():
    """
    Ensure that the first available ip address is returned.
    """
    IPNetFactory.create(ip_net='192.168.1.0/24')

    ip = get_available_own_ip()

    assert IPNet.objects.count() == 1
    assert ip == '192.168.1.1'


@mark.django_db
def test_get_available_own_ip__no_ip_net_configured():
    """
    Ensure that no ip is returned if no IP net is configured.
    """
    ip = get_available_own_ip()

    assert IPNet.objects.count() == 0
    assert ip is None


@mark.django_db
def test_get_available_own_ip__all_ips_taken():
    """
    Ensure that no ip is returned if all ip addresses are taken..
    """
    IPNetFactory.create(ip_net='192.168.1.0/29')
    for i in range(1, 7):
        UserGameserverFactory.create(own_ip=f'192.168.1.{i}')

    ip = get_available_own_ip()

    assert IPNet.objects.count() == 1
    assert UserGameServer.objects.count() == 6
    assert ip is None
