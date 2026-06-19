"""
Modèles de gestion des inventaires.
"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class Inventory(BaseModel):
    """Session d'inventaire."""

    class Status(models.TextChoices):
        PLANNED = 'PLANNED', _('Planifié')
        IN_PROGRESS = 'IN_PROGRESS', _('En cours')
        COMPLETED = 'COMPLETED', _('Terminé')
        VALIDATED = 'VALIDATED', _('Validé')
        CANCELLED = 'CANCELLED', _('Annulé')

    class Type(models.TextChoices):
        FULL = 'FULL', _('Complet')
        PARTIAL = 'PARTIAL', _('Partiel')
        CYCLE = 'CYCLE', _('Tournant')
        SPOT = 'SPOT', _('Ponctuel')

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
        default=Type.FULL
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name=_('entrepôt')
    )
    start_date = models.DateTimeField(_('date début'))
    end_date = models.DateTimeField(_('date fin'), null=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    supervisor = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='supervised_inventories',
        verbose_name=_('superviseur')
    )
    participants = models.ManyToManyField(
        'accounts.User',
        related_name='participated_inventories',
        verbose_name=_('participants'),
        blank=True
    )

    # Résultats
    expected_items = models.IntegerField(_('articles attendus'), default=0)
    counted_items = models.IntegerField(_('articles comptés'), default=0)
    differences = models.IntegerField(_('écarts'), default=0)
    total_value_expected = models.DecimalField(
        _('valeur attendue'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total_value_counted = models.DecimalField(
        _('valeur comptée'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    value_difference = models.DecimalField(
        _('écart de valeur'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('observations'), blank=True)

    class Meta:
        verbose_name = _('inventaire')
        verbose_name_plural = _('inventaires')
        ordering = ['-start_date']
        permissions = [
            ("validate_inventory", "Peut valider un inventaire"),
        ]

    def __str__(self):
        return f"Inventaire {self.reference} - {self.warehouse.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().year
            last = Inventory.objects.filter(
                reference__startswith=f'INV-{year}'
            ).order_by('-reference').first()
            if last:
                num = int(last.reference.split('-')[-1]) + 1
            else:
                num = 1
            self.reference = f'INV-{year}-{num:04d}'
        super().save(*args, **kwargs)


class InventoryLine(BaseModel):
    """Ligne d'inventaire."""

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('inventaire')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='inventory_lines',
        verbose_name=_('produit')
    )
    expected_quantity = models.IntegerField(_('quantité attendue'))
    counted_quantity = models.IntegerField(_('quantité comptée'), null=True, blank=True)
    difference = models.IntegerField(_('écart'), default=0)
    unit_price = models.DecimalField(
        _('prix unitaire'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    difference_value = models.DecimalField(
        _('valeur écart'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    counted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('compté par')
    )
    counted_at = models.DateTimeField(_('compté le'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)

    class Meta:
        verbose_name = _('ligne d\'inventaire')
        verbose_name_plural = _('lignes d\'inventaire')
        unique_together = ['inventory', 'product']

    def save(self, *args, **kwargs):
        if self.counted_quantity is not None:
            self.difference = self.counted_quantity - self.expected_quantity
            self.difference_value = self.difference * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        diff = self.difference if self.difference else '?'
        return f"{self.product.name}: attendu={self.expected_quantity}, compté={self.counted_quantity or '?'}, écart={diff}"
