from random import randint

from factory import Sequence, SubFactory, fuzzy
from factory.django import DjangoModelFactory
from pytest import fixture

from conftest import UserFactory
from server.models import (
    GAMESERVER_ENABLED,
    Game,
    GameSoftware,
    GameSoftwareVersion,
    Node,
    UserGameServer,
)


class GameFactory(DjangoModelFactory):
    title = fuzzy.FuzzyText(length=64)
    min_ram = fuzzy.FuzzyInteger(low=512, high=4096, step=128)
    min_disk_space = fuzzy.FuzzyInteger(low=512, high=4096, step=128)

    class Meta:
        model = Game


class GameSoftwareFactory(DjangoModelFactory):
    game = SubFactory(GameFactory)
    name = fuzzy.FuzzyText(length=64)

    class Meta:
        model = GameSoftware


class GameSoftwareVersionFactory(DjangoModelFactory):
    software = SubFactory(GameSoftwareFactory)
    version = Sequence(lambda n: "1.%s" % randint(1, 20))

    class Meta:
        model = GameSoftwareVersion


class NodeFactory(DjangoModelFactory):
    ip = Sequence(
        lambda n: ".".join(
            [
                str(randint(1, 255)),
                str(randint(1, 255)),
                str(randint(1, 255)),
                str(randint(1, 255)),
            ]
        )
    )
    cores = fuzzy.FuzzyInteger(low=4, high=64)
    ram = fuzzy.FuzzyInteger(low=8192, high=131072, step=2048)
    disk_space = fuzzy.FuzzyInteger(low=81920, high=1310720, step=2048)

    class Meta:
        model = Node


class UserGameserverFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    version = SubFactory(GameSoftwareVersionFactory)
    node = SubFactory(NodeFactory)
    ram = fuzzy.FuzzyInteger(low=512, high=4096, step=512)
    disk_space = fuzzy.FuzzyInteger(low=512, high=8192, step=512)
    status = GAMESERVER_ENABLED

    class Meta:
        model = UserGameServer


@fixture
def minecraft_1_16():
    minecraft = GameFactory.create(title="Minecraft")
    paper = GameSoftwareFactory.create(game=minecraft, name="Paper")
    return GameSoftwareVersionFactory.create(software=paper, version="1.16.5")


@fixture
def user_gameserver():
    return UserGameserverFactory.create()
