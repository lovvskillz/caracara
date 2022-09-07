from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from caraauth.models import User
from caraauth.validators import UsernameValidator


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize a user instance.
    """

    class Meta:
        model = get_user_model()
        fields = ['email', 'username']


class RegisterSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
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
        attrs['user'] = self.create(attrs)
        return attrs
