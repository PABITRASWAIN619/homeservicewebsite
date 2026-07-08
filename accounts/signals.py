from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import AdminProfile


# ==========================================
# CREATE ADMIN PROFILE
# ==========================================

@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        AdminProfile.objects.get_or_create(
            user=instance
        )


# ==========================================
# SAVE ADMIN PROFILE
# ==========================================

@receiver(post_save, sender=User)
def save_admin_profile(sender, instance, **kwargs):
    if instance.is_superuser:
        profile, created = AdminProfile.objects.get_or_create(
            user=instance
        )
        profile.save()