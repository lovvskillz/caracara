from rest_framework.permissions import BasePermission


class IsAnonymous(BasePermission):
    """
    Grant access to anonymous users.
    """

    def has_permission(self, request, view) -> bool:
        return request.user.is_anonymous
