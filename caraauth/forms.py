from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import fields, serializers
from rest_framework.validators import UniqueValidator

from caraauth.models import User
from caraauth.utils.two_fa import confirm_any_device_token
from caraauth.validators import PasswordValidator, UsernameValidator


def token_length_validator(token: str):
    if not len(token) in [6, 8]:
        raise ValidationError(
            _("The token length needs to be 6 or 8 characters long.")
        )


def static_token_length_validator(token: str):
    if len(token) != 8:
        raise ValidationError(
            _("The token length needs to be 8 characters long.")
        )


class OTPForm(forms.Form):
    """
    Form with a field for an OTP.
    """

    otp = fields.CharField(
        required=False,
        allow_blank=True,
        validators=[token_length_validator],
    )

    def __init__(self, *args, **kwargs):
        self.user: User = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_otp(self, otp):
        if not self.user:
            return otp
        if self.user.confirm_any_device_by_otp(otp):
            return otp
        raise ValidationError(_("The given token is not valid."))


class StaticTokenForm(forms.Form):
    """
    Form for a given static token.
    """

    token = fields.CharField(
        validators=[static_token_length_validator],
    )

    def to_representation(self, obj):
        return obj.token


class ConfirmTOTPDeviceForm(OTPForm):
    """
    Confirm a user's TOTP device.
    """

    def clean_otp(self, otp):
        if not self.user:
            return otp
        if self.user.verify_totp_device(otp):
            return otp
        raise ValidationError(_("The given token is not valid."))


class UserForm(forms.ModelForm):
    """
    Form for a user instance.
    """

    class Meta:
        model = get_user_model()
        fields = ['email', 'username']


class UserProfileForm(forms.ModelForm):

    new_password = forms.CharField(validators=[PasswordValidator()], required=False)
    confirm_new_password = forms.CharField(validators=[PasswordValidator()], required=False)

    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
            'new_password',
            'confirm_new_password',
        ]

    def clean(self):
        """
        Run additional validations for user profile data.
        """
        cleaned_data = super().clean()
        if self._validate_new_password(cleaned_data):
            cleaned_data['password'] = make_password(cleaned_data.get('new_password'))
        return cleaned_data

    def _validate_new_password(self, attrs):
        if not (new_password := attrs.get('new_password')):
            return
        if new_password != attrs.get('confirm_new_password'):
            raise ValidationError({'new_password': _("New password does not match!")})
        return True


class RegisterForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'password']
        extra_kwargs = {
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

    def create_user(self) -> 'User':
        """
        Create a new user.
        """
        cleaned_data = self.cleaned_data
        user = get_user_model()(
            email=cleaned_data.get('email'), username=cleaned_data.get('username')
        )
        user.set_password(cleaned_data.get('password'))
        user.save()
        return user


class LoginForm(OTPForm):
    username_or_email = forms.CharField(label=_("Username or email address"), max_length=254)
    password = forms.CharField(validators=[PasswordValidator()], max_length=128)

    class Meta:
        fields = ['username_or_email', 'password', 'otp']

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')
        token = cleaned_data.get('otp', '')
        user = authenticate(username=username_or_email, password=password)
        if not user:
            raise ValidationError(
                message=_(
                    "No account was found with this username / email address and"
                    " password!"
                ),
                code='authorization',
            )
        if not user.is_active:
            raise ValidationError(
                message=_("This account is inactive."),
                code='authorization',
            )
        if user.has_2fa_enabled and not confirm_any_device_token(user, token):
            self.add_error('otp', ValidationError(message=_("Token is not valid", code='authorization')))
            return cleaned_data
        user.update_last_login()
        user.save()
        cleaned_data['user'] = user
        return cleaned_data
