from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        if username is None:
            return None

        try:
            # First try email login
            user = User.objects.get(email=username)

        except User.DoesNotExist:

            try:
                # Then try normal username login (admin)
                user = User.objects.get(username=username)

            except User.DoesNotExist:
                return None


        # Check password
        if password:

            if user.check_password(password):
                return user

            return None


        return user