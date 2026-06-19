"""
Modèles de gestion des entrepôts.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class Warehouse(BaseModel):
    """Entrepôt de stockage."""

    class Type(models.TextChoices):
        MAIN = 'MAIN', _('Principal')
        SECONDARY = 'SECONDARY', _('Secondaire')
        MOBILE = 'MOBILE', _('Mobile')
        VIRTUAL = 'VIRTUAL', _('Virtuel')

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Actif')
        MAINTENANCE = 'MAINTENANCE', _('En maintenance')
        CLOSED = 'CLOSED', _('Fermé')

    name = models.CharField(_('nom'), max_length=200)
    code = models.CharField(_('code'), max_length=20, unique=True)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=Type.choices,
        default=Type.SECONDARY
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    campus = models.ForeignKey(
        'campuses.Campus',
        on_delete=models.CASCADE,
        related_name='warehouses',
        verbose_name=_('campus')
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='warehouses',
        verbose_name=_('département')
    )
    address = models.TextField(_('adresse'), blank=True)
    capacity = models.DecimalField(
        _('capacité (m²)'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_warehouses',
        verbose_name=_('gestionnaire')
    )
    is_temperature_controlled = models.BooleanField(
        _('température contrôlée'),
        default=False
    )
    temperature_min = models.DecimalField(
        _('température min (°C)'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    temperature_max = models.DecimalField(
        _('température max (°C)'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    opening_hours = models.JSONField(
        _('heures d\'ouverture'),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _('entrepôt')
        verbose_name_plural = _('entrepôts')
        ordering = ['campus', 'name']
        permissions = [
            ("manage_warehouse", "Peut gérer l'entrepôt"),
            ("view_warehouse_stock", "Peut voir le stock de l'entrepôt"),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
