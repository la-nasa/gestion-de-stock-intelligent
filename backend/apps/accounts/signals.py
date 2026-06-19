"""
Signaux pour le module accounts.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from apps.accounts.models import User, LoginHistory


@receiver(pre_save, sender=User)
def track_password_change(sender, instance, **kwargs):
    """Suivi des changements de mot de passe."""
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            if old_user.password != instance.password:
                instance.password_changed_at = timezone.now()
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    """Crée une notification de bienvenue."""
    if created:
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=instance,
            type='INFO',
            channel='IN_APP',
            title='Bienvenue sur IUC Inventory !',
            message=f'Bonjour {instance.first_name}, votre compte a été créé avec succès.',
            priority=0
        )
