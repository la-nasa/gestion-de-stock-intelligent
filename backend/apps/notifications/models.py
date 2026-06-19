"""
Modèles de notifications.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel


class Notification(BaseModel):
    """Notification utilisateur."""

    class Type(models.TextChoices):
        INFO = 'INFO', _('Information')
        WARNING = 'WARNING', _('Avertissement')
        ERROR = 'ERROR', _('Erreur')
        SUCCESS = 'SUCCESS', _('Succès')
        STOCK_LOW = 'STOCK_LOW', _('Stock bas')
        STOCK_OUT = 'STOCK_OUT', _('Rupture de stock')
        ORDER_RECEIVED = 'ORDER_RECEIVED', _('Commande reçue')
        ORDER_SHIPPED = 'ORDER_SHIPPED', _('Commande expédiée')
        INVENTORY_DUE = 'INVENTORY_DUE', _('Inventaire à faire')
        MAINTENANCE_DUE = 'MAINTENANCE_DUE', _('Maintenance à faire')
        ANOMALY = 'ANOMALY', _('Anomalie détectée')

    class Channel(models.TextChoices):
        IN_APP = 'IN_APP', _('Dans l\'application')
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
        PUSH = 'PUSH', _('Push')

    recipient = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('destinataire')
    )
    type = models.CharField(
        _('type'),
        max_length=30,
        choices=Type.choices,
        default=Type.INFO
    )
    channel = models.CharField(
        _('canal'),
        max_length=20,
        choices=Channel.choices,
        default=Channel.IN_APP
    )
    title = models.CharField(_('titre'), max_length=200)
    message = models.TextField(_('message'))
    link = models.URLField(_('lien'), blank=True)
    is_read = models.BooleanField(_('lu'), default=False, db_index=True)
    read_at = models.DateTimeField(_('lu le'), null=True, blank=True)
    is_sent = models.BooleanField(_('envoyé'), default=True)
    sent_at = models.DateTimeField(_('envoyé le'), null=True, blank=True)
    priority = models.IntegerField(_('priorité'), default=0)
    related_object_type = models.CharField(
        _('type objet lié'),
        max_length=50,
        blank=True
    )
    related_object_id = models.UUIDField(
        _('ID objet lié'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['type']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"[{self.type}] {self.title} → {self.recipient}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


from django.utils import timezone
