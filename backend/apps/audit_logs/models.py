"""
Modèles pour les logs d'audit.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from core.models.base import BaseModel


class AuditLog(BaseModel):
    """Log d'audit détaillé."""

    class Action(models.TextChoices):
        CREATE = 'CREATE', _('Création')
        UPDATE = 'UPDATE', _('Modification')
        DELETE = 'DELETE', _('Suppression')
        LOGIN = 'LOGIN', _('Connexion')
        LOGOUT = 'LOGOUT', _('Déconnexion')
        EXPORT = 'EXPORT', _('Export')
        IMPORT = 'IMPORT', _('Import')
        VIEW = 'VIEW', _('Consultation')
        APPROVE = 'APPROVE', _('Approbation')
        REJECT = 'REJECT', _('Rejet')
        OTHER = 'OTHER', _('Autre')

    class Severity(models.TextChoices):
        INFO = 'INFO', _('Information')
        WARNING = 'WARNING', _('Avertissement')
        ERROR = 'ERROR', _('Erreur')
        CRITICAL = 'CRITICAL', _('Critique')

    # Identifiants
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name=_('utilisateur')
    )
    user_email = models.CharField(
        _('email utilisateur'),
        max_length=254,
        blank=True,
        help_text="Email de l'utilisateur au moment de l'action"
    )
    user_role = models.CharField(
        _('rôle utilisateur'),
        max_length=50,
        blank=True
    )

    # Action
    action = models.CharField(
        _('action'),
        max_length=20,
        choices=Action.choices,
        default=Action.OTHER
    )
    severity = models.CharField(
        _('sévérité'),
        max_length=20,
        choices=Severity.choices,
        default=Severity.INFO
    )
    module = models.CharField(_('module'), max_length=100)
    description = models.TextField(_('description'))
    ip_address = models.GenericIPAddressField(
        _('adresse IP'),
        null=True,
        blank=True
    )
    user_agent = models.TextField(_('user agent'), blank=True)

    # Objet concerné
    content_type = models.CharField(
        _('type de contenu'),
        max_length=100,
        blank=True,
        help_text="Modèle concerné (ex: 'products.Product')"
    )
    object_id = models.CharField(
        _('ID objet'),
        max_length=100,
        blank=True,
        help_text="UUID ou clé primaire de l'objet"
    )
    object_repr = models.CharField(
        _('représentation objet'),
        max_length=500,
        blank=True
    )

    # Données avant/après
    old_values = models.JSONField(
        _('anciennes valeurs'),
        default=dict,
        blank=True,
        help_text="Valeurs avant modification"
    )
    new_values = models.JSONField(
        _('nouvelles valeurs'),
        default=dict,
        blank=True,
        help_text="Valeurs après modification"
    )
    changes = models.JSONField(
        _('changements'),
        default=dict,
        blank=True,
        help_text="Diff entre anciennes et nouvelles valeurs"
    )

    # Métadonnées
    request_method = models.CharField(
        _('méthode HTTP'),
        max_length=10,
        blank=True
    )
    request_path = models.CharField(
        _('chemin requête'),
        max_length=500,
        blank=True
    )
    response_status = models.IntegerField(
        _('statut réponse'),
        null=True,
        blank=True
    )
    duration_ms = models.IntegerField(
        _('durée (ms)'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('log d\'audit')
        verbose_name_plural = _('logs d\'audit')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['module']),
            models.Index(fields=['severity']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.action} - {self.user_email} - {self.module}"

    def save(self, *args, **kwargs):
        if self.user and not self.user_email:
            self.user_email = self.user.email
        if self.user and not self.user_role:
            self.user_role = self.user.role
        super().save(*args, **kwargs)


class AuditLogArchive(BaseModel):
    """Archive des logs d'audit (après 90 jours)."""

    original_id = models.UUIDField(unique=True)
    archive_date = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    class Meta:
        verbose_name = _('archive log audit')
        verbose_name_plural = _('archives logs audit')
        ordering = ['-archive_date']
