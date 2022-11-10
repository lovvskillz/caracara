from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from caraauth.models import User
from caraauth.utils.two_fa import confirm_any_device_token
from caraauth.validators import PasswordValidator, UsernameValidator


def token_length_validator(token: str):
    if not len(token) in [6, 8]:
        raise serializers.ValidationError(
            _("The token length needs to be 6 or 8 characters long.")
        )


def static_token_length_validator(token: str):
    if len(token) != 8:
        raise serializers.ValidationError(
            _("The token length needs to be 8 characters long.")
        )


class OTPSerializer(serializers.Serializer):
    """
    Serialize a given otp.
    """

    otp = fields.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        validators=[token_length_validator],
    )

    def __init__(self, *args, **kwargs):
        self.user: User = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def validate_otp(self, otp):
        if not self.user:
            return otp
        if self.user.confirm_any_device_by_otp(otp):
            return otp
        raise ValidationError(_("The given token is not valid."))


class StaticTokenSerializer(serializers.Serializer):
    """
    Serialize a given static token.
    """

    token = fields.CharField(
        validators=[static_token_length_validator],
    )

    def to_representation(self, obj):
        return obj.token


class ConfirmTOTPDeviceSerializer(OTPSerializer):
    """
    Confirm a user's TOTP device.
    """

    def validate_otp(self, otp):
        if not self.user:
            return otp
        if self.user.verify_totp_device(otp):
            return otp
        raise ValidationError(_("The given token is not valid."))


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize a user instance.
    """

    class Meta:
        model = get_user_model()
        fields = ['email', 'username']


class UserProfileSerializer(serializers.ModelSerializer):

    new_password = fields.CharField(
        write_only=True, validators=[PasswordValidator()], required=False
    )
    confirm_new_password = fields.CharField(
        write_only=True, validators=[PasswordValidator()], required=False
    )

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'username',
            'has_2fa_enabled',
            'new_password',
            'confirm_new_password',
        ]

    def validate(self, attrs):
        """
        Run additional validations for user profile data.
        """
        attrs = super().validate(attrs)
        if self._validate_new_password(attrs):
            attrs['password'] = make_password(attrs.get('new_password'))
        return attrs

    def _validate_new_password(self, attrs):
        if not (new_password := attrs.get('new_password')):
            return
        if new_password != attrs.get('confirm_new_password'):
            raise ValidationError({'new_password': _("New password does not match!")})
        return True


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
                        queryset=get_user_model().objects.all(),
                        lookup='iexact',
                        message=_("This username is already taken."),
                    ),
                ]
            },
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=get_user_model().objects.all(),
                        lookup='iexact',
                        message=_("This email address is already taken."),
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


class LoginSerializer(serializers.ModelSerializer, OTPSerializer):
    username = serializers.CharField(
        label=_("Username or email address"), max_length=254
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'otp']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def validate(self, attrs):
        username_or_email = attrs.get('username')
        password = attrs.get('password')
        token = attrs.get('otp', '')
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
        if not user.is_active:
            raise serializers.ValidationError(
                detail=_("This account is inactive."),
                code='authorization',
            )
        if user.has_2fa_enabled and not confirm_any_device_token(user, token):
            raise serializers.ValidationError(
                detail={'otp': _("Token is not valid")}, code='authorization'
            )
        attrs['user'] = user
        return attrs
