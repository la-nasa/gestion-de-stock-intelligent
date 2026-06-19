"""
Modèles de gestion des fournisseurs.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class Supplier(BaseModel):
    """Fournisseur de produits."""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Actif')
        INACTIVE = 'INACTIVE', _('Inactif')
        BLACKLISTED = 'BLACKLISTED', _('Liste noire')
        PENDING = 'PENDING', _('En attente')

    # Informations générales
    name = models.CharField(_('nom'), max_length=200)
    code = models.CharField(_('code'), max_length=50, unique=True)
    tax_id = models.CharField(_('numéro contribuable'), max_length=50, blank=True)
    registration_number = models.CharField(
        _('numéro registre commerce'),
        max_length=50,
        blank=True
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    category = models.CharField(_('catégorie'), max_length=100, blank=True)

    # Contact
    contact_person = models.CharField(_('personne contact'), max_length=200, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('téléphone'), max_length=50, blank=True)
    website = models.URLField(_('site web'), blank=True)
    address = models.TextField(_('adresse'), blank=True)
    city = models.CharField(_('ville'), max_length=100, blank=True)
    country = models.CharField(_('pays'), max_length=100, default='Cameroun')

    # Informations bancaires
    bank_name = models.CharField(_('banque'), max_length=200, blank=True)
    bank_account = models.CharField(_('compte bancaire'), max_length=50, blank=True)
    bank_iban = models.CharField(_('IBAN'), max_length=50, blank=True)

    # Conditions commerciales
    payment_terms = models.CharField(
        _('conditions de paiement'),
        max_length=200,
        blank=True
    )
    delivery_time_days = models.IntegerField(
        _('délai de livraison (jours)'),
        default=7
    )
    minimum_order = models.DecimalField(
        _('commande minimum'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    rating = models.IntegerField(_('évaluation'), default=0)

    # Documents
    contract = models.FileField(
        _('contrat'),
        upload_to='contracts/%Y/%m/',
        blank=True,
        null=True
    )
    notes = models.TextField(_('notes'), blank=True)

    class Meta:
        verbose_name = _('fournisseur')
        verbose_name_plural = _('fournisseurs')
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
