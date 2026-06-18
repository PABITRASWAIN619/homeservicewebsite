from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authenticate using email instead of username.
    Works for OTP + password login (safe + clean)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # email comes in "username" field internally
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        # if password is provided (normal login case)
        if password:
            if user.check_password(password):
                return user
            return None

        # OTP login case (no password)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None