from pytest import mark

from server.conftest import NodeFactory, UserGameserverFactory
from server.models import Node


@mark.django_db
def test__enough_available_space():
    """
    Ensure that only nodes with enough available space are being returned.
    """
    node_1, node_2 = NodeFactory.create_batch(2, ram=4096, disk_space=4096)
    UserGameserverFactory.create(ram=2048, disk_space=4096, node=node_1)
    UserGameserverFactory.create(ram=1024, disk_space=512, node=node_2)
    UserGameserverFactory.create(ram=1024, disk_space=512, node=node_2)

    available_nodes = Node.objects.enough_available_space(ram=2048, disk_space=2048)

    assert available_nodes.count() == 1
    assert available_nodes.first() == node_2
