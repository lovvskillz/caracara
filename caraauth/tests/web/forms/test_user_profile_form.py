from pytest import mark

from caraauth.forms import UserProfileForm


@mark.django_db
def test__new_password_validation(user):
    user_data = user.get_profile_as_dict()
    user_data["new_password"] = "S3cretNewPassword"
    user_data["confirm_new_password"] = "S3cretNewPassword"

    form = UserProfileForm(instance=user, data=user_data)

    assert form.is_valid()


@mark.django_db
def test__different_new_password(user):
    user_data = user.get_profile_as_dict()
    user_data["new_password"] = "S3cretNewPassword"
    user_data["confirm_new_password"] = "N0tTheSamePassword"

    form = UserProfileForm(instance=user, data=user_data)

    assert not form.is_valid()
    assert form.errors == {"new_password": ["New password does not match!"]}
