from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.permissions import BasePermission


class IsAnonymous(BasePermission):
    """
    Grant access to anonymous users.
    """

    def has_permission(self, request, view) -> bool:
        return request.user.is_anonymous


class AnonymousRequiredMixin(AccessMixin):
    """
    Grant access to anonymous users. Redirect authenticated users to USER_DASHBOARD_URL page.
    Use in TemplateViews.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse(settings.USER_DASHBOARD_URL))
        return super().dispatch(request, *args, **kwargs)
