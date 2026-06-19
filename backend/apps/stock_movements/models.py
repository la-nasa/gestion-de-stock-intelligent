"""
Modèles de gestion des stocks.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class Stock(BaseModel):
    """Stock d'un produit dans un entrepôt."""

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name=_('produit')
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name=_('entrepôt')
    )
    quantity = models.IntegerField(_('quantité'), default=0)
    reserved_quantity = models.IntegerField(_('quantité réservée'), default=0)
    available_quantity = models.IntegerField(_('quantité disponible'), default=0)
    unit_price = models.DecimalField(
        _('prix unitaire'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    location = models.CharField(
        _('emplacement'),
        max_length=100,
        blank=True,
        help_text='Rayon, étagère, etc.'
    )
    last_inventory_date = models.DateTimeField(
        _('dernier inventaire'),
        null=True,
        blank=True
    )
    last_movement_date = models.DateTimeField(
        _('dernier mouvement'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('stock')
        verbose_name_plural = _('stocks')
        unique_together = ['product', 'warehouse']
        ordering = ['warehouse', 'product__category', 'product__name']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['quantity']),
            models.Index(fields=['last_movement_date']),
        ]

    def __str__(self):
        return f"{self.product.name} @ {self.warehouse.name}: {self.quantity}"

    def save(self, *args, **kwargs):
        self.available_quantity = self.quantity - self.reserved_quantity
        super().save(*args, **kwargs)

    @property
    def total_value(self):
        return self.quantity * self.unit_price

    @property
    def is_low(self):
        return self.quantity <= self.product.min_stock


class StockMovement(BaseModel):
    """Mouvement de stock (entrée ou sortie)."""

    class MovementType(models.TextChoices):
        ENTRY = 'ENTRY', _('Entrée')
        OUTPUT = 'OUTPUT', _('Sortie')
        TRANSFER = 'TRANSFER', _('Transfert')
        ADJUSTMENT = 'ADJUSTMENT', _('Ajustement')
        RETURN = 'RETURN', _('Retour')

    class Reason(models.TextChoices):
        PURCHASE = 'PURCHASE', _('Achat')
        SALE = 'SALE', _('Vente')
        INTERNAL_USE = 'INTERNAL_USE', _('Usage interne')
        DONATION = 'DONATION', _('Don')
        DAMAGE = 'DAMAGE', _('Dommage')
        LOSS = 'LOSS', _('Perte')
        RETURN_SUPPLIER = 'RETURN_SUPPLIER', _('Retour fournisseur')
        INVENTORY_ADJUSTMENT = 'INVENTORY_ADJUSTMENT', _('Ajustement inventaire')
        OTHER = 'OTHER', _('Autre')

    movement_type = models.CharField(
        _('type de mouvement'),
        max_length=20,
        choices=MovementType.choices
    )
    reason = models.CharField(
        _('raison'),
        max_length=50,
        choices=Reason.choices,
        default=Reason.OTHER
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_('stock')
    )
    quantity = models.IntegerField(_('quantité'))
    unit_price = models.DecimalField(
        _('prix unitaire'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total_price = models.DecimalField(
        _('prix total'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    reference_document = models.CharField(
        _('document de référence'),
        max_length=100,
        blank=True
    )
    performed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_movements',
        verbose_name=_('effectué par')
    )
    validated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_movements',
        verbose_name=_('validé par')
    )
    validated_at = models.DateTimeField(_('validé le'), null=True, blank=True)
    is_validated = models.BooleanField(_('validé'), default=False)
    notes = models.TextField(_('notes'), blank=True)

    class Meta:
        verbose_name = _('mouvement de stock')
        verbose_name_plural = _('mouvements de stock')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock', '-created_at']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['-created_at']),
        ]
        permissions = [
            ("validate_movement", "Peut valider un mouvement"),
            ("cancel_movement", "Peut annuler un mouvement"),
        ]

    def __str__(self):
        direction = '+' if self.movement_type in ['ENTRY', 'RETURN'] else '-'
        return f"{direction}{self.quantity} {self.stock.product.name} ({self.reason})"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def validate(self, user):
        self.is_validated = True
        self.validated_by = user
        self.validated_at = timezone.now()
        self.save()
        self.update_stock()

    def update_stock(self):
        if self.movement_type in ['ENTRY', 'RETURN']:
            self.stock.quantity += self.quantity
        elif self.movement_type in ['OUTPUT', 'TRANSFER', 'LOSS', 'DAMAGE']:
            self.stock.quantity -= self.quantity
        self.stock.last_movement_date = timezone.now()
        self.stock.save()


# Importer timezone ici pour la méthode validate
from django.utils import timezone
