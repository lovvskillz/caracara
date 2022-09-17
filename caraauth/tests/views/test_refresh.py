from pytest import mark
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

REFRESH_URL = reverse('auth:refresh')


@mark.django_db
def test_refresh_token(apitest, user):
    """
    Ensure that users with valid refresh token can obtain a new access token.
    """
    token = RefreshToken.for_user(user)

    response = apitest().post(REFRESH_URL, data={'refresh': str(token)})

    assert response.status_code == status.HTTP_200_OK
    assert 'refresh' in response.data
    assert JWTAuthentication().get_validated_token(response.data['access'])


@mark.django_db
def test_refresh_token_required(apitest):
    """
    Ensure that refresh token is required.
    """
    response = apitest().post(REFRESH_URL)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['refresh'] == [
        ErrorDetail(string="This field is required.", code='required')
    ]


@mark.django_db
def test_refresh_token_is_invalid(apitest):
    """
    Ensure that an invalid refresh token will not return an access token.
    """
    response = apitest().post(REFRESH_URL, data={'refresh': 'invalid'})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {
        'detail': ErrorDetail(
            string="Token is invalid or expired", code='token_not_valid'
        ),
        'code': ErrorDetail(string='token_not_valid', code='token_not_valid'),
    }


@mark.django_db
def test_refresh_token_is_expired(apitest, user, freezer):
    """
    Ensure that an expired refresh token will not return an access token.
    """
    freezer.move_to('2022-09-01')
    token = RefreshToken.for_user(user)
    freezer.move_to('2022-09-30')  # refresh token should be invalid

    response = apitest().post(REFRESH_URL, data={'refresh': str(token)})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {
        'detail': ErrorDetail(
            string="Token is invalid or expired", code='token_not_valid'
        ),
        'code': ErrorDetail(string='token_not_valid', code='token_not_valid'),
    }
