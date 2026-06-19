"""
Modèles pour les entrées de stock.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class StockEntry(BaseModel):
    """Bon d'entrée de stock."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Brouillon')
        VALIDATED = 'VALIDATED', _('Validé')
        CANCELLED = 'CANCELLED', _('Annulé')

    reference = models.CharField(
        _('référence'),
        max_length=50,
        unique=True,
        db_index=True
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.PROTECT,
        related_name='stock_entries',
        verbose_name=_('entrepôt')
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_entries',
        verbose_name=_('fournisseur')
    )
    purchase_order = models.ForeignKey(
        'purchase_orders.PurchaseOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_entries',
        verbose_name=_('bon de commande')
    )
    delivery_note = models.CharField(
        _('bon de livraison'),
        max_length=100,
        blank=True
    )
    invoice_number = models.CharField(
        _('numéro facture'),
        max_length=100,
        blank=True
    )
    entry_date = models.DateTimeField(_('date d\'entrée'), auto_now_add=True)
    received_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_entries',
        verbose_name=_('reçu par')
    )
    validated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_entries',
        verbose_name=_('validé par')
    )
    validated_at = models.DateTimeField(_('validé le'), null=True, blank=True)
    total_amount = models.DecimalField(
        _('montant total'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('notes'), blank=True)

    class Meta:
        verbose_name = _('entrée de stock')
        verbose_name_plural = _('entrées de stock')
        ordering = ['-entry_date']

    def __str__(self):
        return f"ENT-{self.reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            from django.utils import timezone
            year = timezone.now().year
            last = StockEntry.objects.filter(
                reference__startswith=f'ENT-{year}'
            ).order_by('-reference').first()
            if last:
                num = int(last.reference.split('-')[-1]) + 1
            else:
                num = 1
            self.reference = f'ENT-{year}-{num:04d}'
        super().save(*args, **kwargs)


class StockEntryLine(BaseModel):
    """Ligne d'entrée de stock."""

    entry = models.ForeignKey(
        StockEntry,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('entrée')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='entry_lines',
        verbose_name=_('produit')
    )
    quantity = models.IntegerField(_('quantité'))
    unit_price = models.DecimalField(
        _('prix unitaire'),
        max_digits=15,
        decimal_places=2
    )
    total_price = models.DecimalField(
        _('prix total'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    location = models.CharField(
        _('emplacement'),
        max_length=100,
        blank=True
    )
    batch_number = models.CharField(
        _('numéro de lot'),
        max_length=100,
        blank=True
    )
    expiry_date = models.DateField(
        _('date d\'expiration'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('ligne d\'entrée')
        verbose_name_plural = _('lignes d\'entrée')

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
