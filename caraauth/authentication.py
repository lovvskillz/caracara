from rest_framework.permissions import IsAuthenticated


def user_authentication_rule(user):
    """
    Allow authentication for active users.
    """
    return user is not None and user.is_active


class Has2FADisabled(IsAuthenticated):
    """
    Allow access only to authenticated users without 2FA enabled.
    """

    def has_permission(self, request, view):
        twofa_disabled = (
            super().has_permission(request, view) and not request.user.has_2fa_enabled
        )
        return twofa_disabled


class Has2FAEnabled(IsAuthenticated):
    """
    Allow access only to authenticated users with 2FA enabled.
    """

    def has_permission(self, request, view):
        twofa_enabled = (
            super().has_permission(request, view) and request.user.has_2fa_enabled
        )
        return twofa_enabled
