"""
Custom authentication backend: authenticate by email instead of username.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """Authenticate using email address."""

    def authenticate(self, request, email=None, password=None, **kwargs):
        # Also handle 'username' kwarg for admin panel compatibility
        if email is None:
            email = kwargs.get("username")
        if email is None:
            return None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Run the password hasher to prevent timing attacks
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
