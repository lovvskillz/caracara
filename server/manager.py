from typing import TYPE_CHECKING

from django.db.models import F, Sum

from carautils.utils.db.managers import BaseManager, BaseQuerySet

if TYPE_CHECKING:
    from caraauth.models import User
    from server.models import Node


class IPNetQuerySet(BaseQuerySet):
    def active(self):
        """
        Return active IPNet objects.
        """
        return self.filter(active=True)


class IPNetManager(BaseManager.from_queryset(IPNetQuerySet)):
    pass


class NodeQuerySet(BaseQuerySet):
    def enough_available_space(self, ram: int, disk_space: int):
        """
        Filter nodes with enough free space for given RAM and disk space.
        """
        return (
            self.prefetch_related('game_servers')
            .annotate(
                used_ram=Sum('game_servers__ram', default=0),
                used_disk_space=Sum('game_servers__disk_space', default=0),
                remaining_ram=F('ram') - F('used_ram'),
                remaining_disk_space=F('disk_space') - F('used_disk_space'),
            )
            .filter(remaining_ram__gte=ram, remaining_disk_space__gte=disk_space)
        )


class NodeManager(BaseManager.from_queryset(NodeQuerySet)):
    pass


class UserGameserverQuerySet(BaseQuerySet):
    def own_ip(self):
        """
        Return game servers with an own ip address.
        """
        return self.filter(own_ip__isnull=False)

    def from_user(self, user: 'User'):
        """
        Return game servers of given user.
        """
        return self.filter(user=user)

    def hosted_on_node(self, node: 'Node'):
        return self.filter(node=node)


class UserGameserverManager(BaseManager.from_queryset(UserGameserverQuerySet)):
    pass
