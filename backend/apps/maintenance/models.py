"""
Modèles de gestion de la maintenance.
"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class MaintenanceRecord(BaseModel):
    """Enregistrement de maintenance d'un équipement."""

    class Type(models.TextChoices):
        PREVENTIVE = 'PREVENTIVE', _('Préventive')
        CORRECTIVE = 'CORRECTIVE', _('Corrective')
        PREDICTIVE = 'PREDICTIVE', _('Prédictive')
        CALIBRATION = 'CALIBRATION', _('Calibration')
        INSPECTION = 'INSPECTION', _('Inspection')

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Planifiée')
        IN_PROGRESS = 'IN_PROGRESS', _('En cours')
        COMPLETED = 'COMPLETED', _('Terminée')
        CANCELLED = 'CANCELLED', _('Annulée')
        OVERDUE = 'OVERDUE', _('En retard')

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='maintenance_records',
        verbose_name=_('produit/équipement')
    )
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
        default=Type.PREVENTIVE
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    description = models.TextField(_('description du problème'))
    actions_taken = models.TextField(_('actions effectuées'), blank=True)
    technician = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_maintenance',
        verbose_name=_('technicien')
    )
    scheduled_date = models.DateTimeField(_('date planifiée'))
    started_at = models.DateTimeField(_('début'), null=True, blank=True)
    completed_at = models.DateTimeField(_('fin'), null=True, blank=True)
    cost = models.DecimalField(
        _('coût'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    duration_minutes = models.IntegerField(
        _('durée (minutes)'),
        null=True,
        blank=True
    )
    parts_replaced = models.TextField(_('pièces remplacées'), blank=True)
    next_maintenance_date = models.DateTimeField(
        _('prochaine maintenance'),
        null=True,
        blank=True
    )
    notes = models.TextField(_('notes'), blank=True)

    class Meta:
        verbose_name = _('maintenance')
        verbose_name_plural = _('maintenances')
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['product', '-scheduled_date']),
            models.Index(fields=['status']),
            models.Index(fields=['next_maintenance_date']),
        ]

    def __str__(self):
        return f"MAINT-{self.reference} - {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().year
            last = MaintenanceRecord.objects.filter(
                reference__startswith=f'MAINT-{year}'
            ).order_by('-reference').first()
            if last:
                num = int(last.reference.split('-')[-1]) + 1
            else:
                num = 1
            self.reference = f'MAINT-{year}-{num:04d}'
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_minutes = int(delta.total_seconds() / 60)
        super().save(*args, **kwargs)
