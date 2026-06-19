"""
Modèles organisationnels : Départements, Campus.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class Campus(BaseModel):
    """Campus de l'institut."""

    name = models.CharField(_('nom'), max_length=200)
    code = models.CharField(_('code'), max_length=20, unique=True)
    address = models.TextField(_('adresse'), blank=True)
    city = models.CharField(_('ville'), max_length=100, default='Douala')
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    email = models.EmailField(_('email'), blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    latitude = models.DecimalField(
        _('latitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        _('longitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('campus')
        verbose_name_plural = _('campus')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Department(BaseModel):
    """Département de l'institut."""

    class Type(models.TextChoices):
        ACADEMIC = 'ACADEMIC', _('Académique')
        ADMINISTRATIVE = 'ADMINISTRATIVE', _('Administratif')
        TECHNICAL = 'TECHNICAL', _('Technique')
        RESEARCH = 'RESEARCH', _('Recherche')
        OTHER = 'OTHER', _('Autre')

    name = models.CharField(_('nom'), max_length=200)
    code = models.CharField(_('code'), max_length=20, unique=True)
    description = models.TextField(_('description'), blank=True)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=Type.choices,
        default=Type.ACADEMIC
    )
    campus = models.ForeignKey(
        Campus,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name=_('campus')
    )
    head = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        verbose_name=_('responsable')
    )
    is_active = models.BooleanField(_('actif'), default=True)
    budget = models.DecimalField(
        _('budget annuel'),
        max_digits=15,
        decimal_places=2,
        default=0
    )

    class Meta:
        verbose_name = _('département')
        verbose_name_plural = _('départements')
        ordering = ['campus', 'name']

    def __str__(self):
        return f"{self.name} - {self.campus.name}"
