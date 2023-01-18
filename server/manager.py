from django.db.models import F, Sum

from carautils.utils.db.managers import BaseManager, BaseQuerySet


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
                used_ram=Sum('game_servers__ram'),
                used_disk_space=Sum('game_servers__disk_space'),
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


class UserGameserverManager(BaseManager.from_queryset(UserGameserverQuerySet)):
    pass
