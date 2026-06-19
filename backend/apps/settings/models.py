"""
Modèles de paramètres système.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel


class SystemSetting(BaseModel):
    """Paramètre système global."""

    key = models.CharField(
        _('clé'),
        max_length=200,
        unique=True,
        db_index=True
    )
    value = models.TextField(_('valeur'), blank=True)
    value_type = models.CharField(
        _('type de valeur'),
        max_length=20,
        default='string',
        choices=[
            ('string', 'Texte'),
            ('integer', 'Entier'),
            ('float', 'Décimal'),
            ('boolean', 'Booléen'),
            ('json', 'JSON'),
        ]
    )
    description = models.TextField(_('description'), blank=True)
    is_public = models.BooleanField(_('public'), default=False)
    category = models.CharField(
        _('catégorie'),
        max_length=100,
        default='general'
    )

    class Meta:
        verbose_name = _('paramètre système')
        verbose_name_plural = _('paramètres système')
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.key} = {self.value}"

    def get_typed_value(self):
        """Retourne la valeur avec le bon type."""
        if self.value_type == 'integer':
            return int(self.value) if self.value else 0
        elif self.value_type == 'float':
            return float(self.value) if self.value else 0.0
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'oui')
        elif self.value_type == 'json':
            import json
            return json.loads(self.value) if self.value else {}
        return self.value


class NotificationTemplate(BaseModel):
    """Template de notification."""

    code = models.CharField(
        _('code'),
        max_length=100,
        unique=True,
        db_index=True
    )
    name = models.CharField(_('nom'), max_length=200)
    subject_template = models.CharField(
        _('template sujet'),
        max_length=500,
        help_text="Utilise {{ variable }} pour les placeholders"
    )
    body_template = models.TextField(
        _('template corps'),
        help_text="Template HTML ou texte"
    )
    is_active = models.BooleanField(_('actif'), default=True)

    class Meta:
        verbose_name = _('template notification')
        verbose_name_plural = _('templates notification')
        ordering = ['name']

    def __str__(self):
        return self.name


class EmailLog(BaseModel):
    """Historique des emails envoyés."""

    to_email = models.EmailField(_('destinataire'))
    subject = models.CharField(_('sujet'), max_length=500)
    body = models.TextField(_('corps'), blank=True)
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=[
            ('SENT', 'Envoyé'),
            ('FAILED', 'Échec'),
            ('BOUNCED', 'Rebondi'),
            ('OPENED', 'Ouvert'),
        ],
        default='SENT'
    )
    error_message = models.TextField(_('message d\'erreur'), blank=True)
    sent_at = models.DateTimeField(_('envoyé le'), auto_now_add=True)

    class Meta:
        verbose_name = _('log email')
        verbose_name_plural = _('logs email')
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email → {self.to_email}: {self.status}"
