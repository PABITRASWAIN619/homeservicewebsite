from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import AdminProfile, CustomerProfile


# =================================
# CREATE ADMIN PROFILE ONLY FOR ADMIN
# =================================

@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):

    if created and instance.is_superuser:
        AdminProfile.objects.get_or_create(
            user=instance
        )


# =================================
# SAVE ADMIN PROFILE
# =================================

@receiver(post_save, sender=User)
def save_admin_profile(sender, instance, **kwargs):

    if instance.is_superuser:

        profile, created = AdminProfile.objects.get_or_create(
            user=instance
        )

        profile.save()



# =================================
# REMOVE THIS PART
# CUSTOMER PROFILE SHOULD NOT AUTO CREATE
# =================================

# DELETE THIS:

# @receiver(post_save, sender=User)
# def create_customer_profile(sender, instance, created, **kwargs):
#     if created:
#         CustomerProfile.objects.get_or_create(user=instance)


# @receiver(post_save, sender=User)
# def save_customer_profile(sender, instance, **kwargs):
#     profile, created = CustomerProfile.objects.get_or_create(user=instance)
#     profile.save()