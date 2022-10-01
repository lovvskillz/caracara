from durin.models import Client
from durin.views import LoginView as DurinLoginView
from rest_framework.exceptions import NotAcceptable

from caraauth.models import User


class AuthMixin(DurinLoginView):
    serializer_class = None

    def validate_and_return_user(self, request) -> 'User':
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data['user']

    def get_client_obj(self, request) -> 'Client':
        client_name = request.META.get('HTTP_X_API_CLIENT', None)
        if not client_name:
            raise NotAcceptable(detail="Client not set", code='no_api_client')
        try:
            return Client.objects.get(name=client_name)
        except Client.DoesNotExist:
            raise NotAcceptable(
                detail="Es wurde kein API Client mit diesem Namen gefunden",
                code='wrong_api_client',
            )
