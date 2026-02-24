from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
import sys
from .models import User

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either
    their username or their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        sys.stderr.write(f"DEBUG: EmailOrUsernameModelBackend.authenticate called for: {username}\n")
        try:
            # Try to fetch the user by username or email
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
            sys.stderr.write(f"DEBUG: Found user: {user}\n")
        except User.DoesNotExist:
            sys.stderr.write(f"DEBUG: User not found for: {username}\n")
            # Run the default password hasher once to reduce the vulnerability
            # to timing attacks.
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            sys.stderr.write(f"DEBUG: Multiple users found for: {username}\n")
            # If multiple users match (shouldn't happen with unique constraints),
            # pick the one that matches username exactly if possible, or just fail safely.
            user = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()

        if user.check_password(password) and self.user_can_authenticate(user):
            sys.stderr.write(f"DEBUG: Password match and user can authenticate\n")
            return user
        sys.stderr.write(f"DEBUG: Password check failed or user cannot authenticate\n")
        return None
