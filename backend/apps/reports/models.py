"""
Modèles pour les rapports.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class Report(BaseModel):
    """Rapport généré."""

    class Type(models.TextChoices):
        STOCK_LEVEL = 'STOCK_LEVEL', _('Niveau de stock')
        MOVEMENT = 'MOVEMENT', _('Mouvements')
        CONSUMPTION = 'CONSUMPTION', _('Consommation')
        INVENTORY = 'INVENTORY', _('Inventaire')
        PURCHASE = 'PURCHASE', _('Achats')
        FINANCIAL = 'FINANCIAL', _('Financier')
        CUSTOM = 'CUSTOM', _('Personnalisé')

    class Format(models.TextChoices):
        PDF = 'PDF', _('PDF')
        EXCEL = 'EXCEL', _('Excel')
        CSV = 'CSV', _('CSV')
        WORD = 'WORD', _('Word')

    class Status(models.TextChoices):
        GENERATING = 'GENERATING', _('En génération')
        COMPLETED = 'COMPLETED', _('Terminé')
        FAILED = 'FAILED', _('Échoué')

    name = models.CharField(_('nom'), max_length=300)
    reference = models.CharField(
        _('référence'),
        max_length=50,
        unique=True,
        db_index=True
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=Type.choices,
        default=Type.STOCK_LEVEL
    )
    format = models.CharField(
        _('format'),
        max_length=10,
        choices=Format.choices,
        default=Format.PDF
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.GENERATING
    )
    file = models.FileField(
        _('fichier'),
        upload_to='reports/%Y/%m/',
        blank=True,
        null=True
    )
    generated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports',
        verbose_name=_('généré par')
    )
    parameters = models.JSONField(
        _('paramètres'),
        default=dict,
        blank=True
    )
    filters = models.JSONField(
        _('filtres'),
        default=dict,
        blank=True
    )
    data_summary = models.JSONField(
        _('résumé données'),
        default=dict,
        blank=True
    )
    file_size = models.BigIntegerField(
        _('taille fichier'),
        null=True,
        blank=True
    )
    error_message = models.TextField(_('message d\'erreur'), blank=True)

    class Meta:
        verbose_name = _('rapport')
        verbose_name_plural = _('rapports')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type', '-created_at']),
            models.Index(fields=['generated_by', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.reference}"


class ReportSchedule(BaseModel):
    """Planification de rapport."""

    class Frequency(models.TextChoices):
        DAILY = 'DAILY', _('Quotidien')
        WEEKLY = 'WEEKLY', _('Hebdomadaire')
        MONTHLY = 'MONTHLY', _('Mensuel')
        QUARTERLY = 'QUARTERLY', _('Trimestriel')
        YEARLY = 'YEARLY', _('Annuel')

    name = models.CharField(_('nom'), max_length=300)
    report_type = models.CharField(
        _('type de rapport'),
        max_length=20,
        choices=Report.Type.choices
    )
    format = models.CharField(
        _('format'),
        max_length=10,
        choices=Report.Format.choices,
        default=Format.PDF
    )
    frequency = models.CharField(
        _('fréquence'),
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.MONTHLY
    )
    day_of_week = models.IntegerField(
        _('jour de la semaine'),
        null=True,
        blank=True,
        choices=[(i, f'Jour {i}') for i in range(7)]
    )
    day_of_month = models.IntegerField(
        _('jour du mois'),
        null=True,
        blank=True
    )
    time = models.TimeField(_('heure'))
    recipients = models.JSONField(
        _('destinataires'),
        default=list,
        blank=True
    )
    parameters = models.JSONField(
        _('paramètres'),
        default=dict,
        blank=True
    )
    is_active = models.BooleanField(_('actif'), default=True)
    last_generated = models.DateTimeField(
        _('dernière génération'),
        null=True,
        blank=True
    )
    next_generation = models.DateTimeField(
        _('prochaine génération'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('planification rapport')
        verbose_name_plural = _('planifications rapport')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"
