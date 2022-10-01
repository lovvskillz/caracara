from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import fields, serializers
from rest_framework.validators import UniqueValidator

from caraauth.models import User
from caraauth.utils.two_fa import confirm_any_device_token
from caraauth.validators import UsernameValidator


def token_length_validator(token: str):
    if not len(token) in [6, 8]:
        raise serializers.ValidationError(
            _("The token length needs to be 6 or 8 characters long.")
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize a user instance.
    """

    class Meta:
        model = get_user_model()
        fields = ['email', 'username']


class UserProfileSerializer(serializers.ModelSerializer):
    """ """

    new_password = fields.CharField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'new_password', 'has_2fa_enabled']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'username': {
                'validators': [
                    UsernameValidator(),
                    UniqueValidator(
                        queryset=get_user_model().objects.all(), lookup='iexact'
                    ),
                ]
            },
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=get_user_model().objects.all(), lookup='iexact'
                    )
                ]
            },
        }

    def create(self, validated_data) -> 'User':
        """
        Create a new user.
        """
        user = get_user_model()(
            email=validated_data.get('email'), username=validated_data.get('username')
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    def validate(self, attrs):
        user = self.create(attrs)
        attrs['user'] = user
        return attrs


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        label=_("Username or email address"), max_length=254
    )
    otp_token = fields.CharField(
        max_length=8,
        required=False,
        allow_blank=True,
        write_only=True,
        validators=[token_length_validator],
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'otp_token']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def validate(self, attrs):
        username_or_email = attrs.get('username')
        password = attrs.get('password')
        token = attrs.get('otp_token')
        user = authenticate(
            self.context.get('request'), username=username_or_email, password=password
        )
        if not user:
            raise serializers.ValidationError(
                detail=_(
                    "No account was found with this username / email address and"
                    " password!"
                ),
                code='authorization',
            )
        if user.has_2fa_enabled and not confirm_any_device_token(user, token):
            raise serializers.ValidationError(
                detail={'token': _("Token is not valid")}, code='authorization'
            )
        attrs['user'] = user
        return attrs
