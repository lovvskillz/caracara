from django.contrib.auth import get_user_model
from pytest import mark
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse

from caraauth.serializers import UserProfileSerializer

profile_url = reverse('api:user_area:profile')


@mark.django_db
def test__get_user_profile__success(apitest, user):
    """
    Get user profile information.
    """
    user_data = UserProfileSerializer(instance=user).data

    response = apitest(user).get(profile_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user_data


@mark.django_db
def test__get_user_profile__unauthorized(apitest):
    """
    Deny access for unauthorized users.
    """
    response = apitest().get(profile_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.django_db
def test_update_user_profile__success(apitest, user):
    """
    Update user profile successfully.
    """
    user_data_response = UserProfileSerializer(instance=user).data
    user_data_response['username'] = 'new_user_name'
    user_data = user_data_response.copy()
    new_password = 'MyS3CRETPassw0rd'
    user_data.update(
        {'new_password': new_password, 'confirm_new_password': new_password}
    )

    response = apitest(user).post(profile_url, data=user_data)
    updated_user = get_user_model().objects.get()

    assert response.status_code == status.HTTP_200_OK
    assert response.data == user_data_response
    assert updated_user.username == 'new_user_name'
    assert updated_user.check_password(new_password)


@mark.parametrize(
    'data, error',
    [
        (
            {'username': '123'},
            {
                'username': [
                    ErrorDetail(
                        string="Ensure this field has at least 5 characters.",
                        code='min_length',
                    )
                ]
            },
        ),
        (
            {'new_password': 'invalid', 'confirm_new_password': 'invalid'},
            {
                'new_password': [
                    ErrorDetail(
                        string=(
                            "Enter a valid password. Should be at least 8 characters"
                            " long containing letters and numbers."
                        ),
                        code='invalid',
                    )
                ],
                'confirm_new_password': [
                    ErrorDetail(
                        string=(
                            "Enter a valid password. Should be at least 8 characters"
                            " long containing letters and numbers."
                        ),
                        code='invalid',
                    )
                ],
            },
        ),
        (
            {
                'new_password': 'SomeVal1dP4ssword',
                'confirm_new_password': 'N0tTheSameP4ssword',
            },
            {
                'new_password': [
                    ErrorDetail(string="New password does not match!", code='invalid')
                ]
            },
        ),
    ],
)
@mark.django_db
def test_update_user_profile__invalid_data(apitest, user, data, error):
    """
    Error message should be returned with invalid user data submitted and actual data doesn't change.
    """
    user_data = UserProfileSerializer(instance=user).data
    user_data.update(data)

    response = apitest(user).post(profile_url, data=user_data)
    updated_user = get_user_model().objects.get()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == error
    assert updated_user.username == user.username
    assert updated_user.password == user.password
