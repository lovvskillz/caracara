from typing import Optional

from server.models import IPNet, Node, UserGameServer


def get_available_own_ip() -> Optional[str]:
    """
    Return the next available own ip address.
    """
    taken_ips = (
        UserGameServer.objects.own_ip()
        .values_list('own_ip', flat=True)
        .order_by('own_ip')
    )

    for ip_net in IPNet.objects.active():
        prefix, suffix = ip_net.split_cidr_notation()
        last_byte = prefix.split('.')[3]
        first_available_number = int(last_byte) + 1
        last_available_number = 2 ** (32 - suffix) - 1
        ips = (
            f'{prefix.rsplit(last_byte, 1)[0]}{i}'
            for i in range(first_available_number, last_available_number)
        )
        return next(filter(lambda ip: ip not in taken_ips, ips), None)

    return None


def get_node_for_hosting(ram: int, disk_space: int) -> 'Node':
    """
    Get a node with enough available capacity.
    """
    return Node.objects.enough_available_space(ram, disk_space).first()
