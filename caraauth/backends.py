from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class UsernameOrEmailModelBackend(ModelBackend):
    def authenticate(
        self, request, username=None, password=None, **kwargs
    ) -> Optional[UserModel]:
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        lookup = {f'{("email" if "@" in username else "username")}__iexact': username}
        try:
            user = UserModel._default_manager.get(**lookup)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
