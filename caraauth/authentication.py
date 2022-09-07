def user_authentication_rule(user):
    """
    Allow authentication for active users.
    """
    return user is not None and user.is_active
