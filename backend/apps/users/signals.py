from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User


@receiver(post_save, sender=User)
def sync_user_role_reference(sender, instance, **kwargs):
    if instance.role_ref_id:
        legacy = instance.role_ref.name.upper()
        if instance.role != legacy:
            User.objects.filter(pk=instance.pk).update(role=legacy)
