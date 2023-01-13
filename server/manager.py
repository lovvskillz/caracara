from django.db.models import Manager, QuerySet


class IPNetQuerySet(QuerySet):
    def active(self):
        """
        Return active IPNet objects.
        """
        return self.filter(active=True)


class IPNetManager(Manager.from_queryset(IPNetQuerySet)):
    pass


class UserGameserverQuerySet(QuerySet):
    def own_ip(self):
        """
        Return game servers with an own ip address.
        """
        return self.filter(own_ip__isnull=False)


class UserGameserverManager(Manager.from_queryset(UserGameserverQuerySet)):
    pass
