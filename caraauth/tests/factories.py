from factory import Sequence, post_generation
from factory.django import DjangoModelFactory
from pytest_factoryboy import register


@register
class UserFactory(DjangoModelFactory):
    username = Sequence(lambda n: f"some_user_{n}")
    email = Sequence(lambda n: f"some.user{n}@example.com")
    is_superuser = False
    is_active = True

    class Meta:
        model = "caraauth.User"

    @post_generation
    def password(self, create, extracted, **kwargs):
        if create:
            self.set_password(extracted)
            self.save()
