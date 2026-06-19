"""
Modèles de gestion des commandes fournisseurs.
"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class PurchaseOrder(BaseModel):
    """Bon de commande fournisseur."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Brouillon')
        PENDING = 'PENDING', _('En attente')
        APPROVED = 'APPROVED', _('Approuvée')
        ORDERED = 'ORDERED', _('Commandée')
        PARTIALLY_RECEIVED = 'PARTIALLY_RECEIVED', _('Reçue partiellement')
        RECEIVED = 'RECEIVED', _('Reçue')
        CANCELLED = 'CANCELLED', _('Annulée')
        REJECTED = 'REJECTED', _('Rejetée')

    reference = models.CharField(
        _('référence'),
        max_length=50,
        unique=True,
        db_index=True
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        verbose_name=_('fournisseur')
    )
    status = models.CharField(
        _('statut'),
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT
    )
    order_date = models.DateField(_('date de commande'), default=timezone.now)
    expected_delivery_date = models.DateField(
        _('date de livraison prévue'),
        null=True,
        blank=True
    )
    actual_delivery_date = models.DateField(
        _('date de livraison réelle'),
        null=True,
        blank=True
    )
    total_amount = models.DecimalField(
        _('montant total'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        _('TVA'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    shipping_cost = models.DecimalField(
        _('frais de livraison'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('notes'), blank=True)
    requested_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='requested_orders',
        verbose_name=_('demandé par')
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_orders',
        verbose_name=_('approuvé par')
    )
    approved_at = models.DateTimeField(_('approuvé le'), null=True, blank=True)
    attachment = models.FileField(
        _('pièce jointe'),
        upload_to='purchase_orders/%Y/%m/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('bon de commande')
        verbose_name_plural = _('bons de commande')
        ordering = ['-order_date']
        permissions = [
            ("approve_order", "Peut approuver une commande"),
        ]

    def __str__(self):
        return f"BC-{self.reference} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().year
            last = PurchaseOrder.objects.filter(
                reference__startswith=f'BC-{year}'
            ).order_by('-reference').first()
            if last:
                num = int(last.reference.split('-')[-1]) + 1
            else:
                num = 1
            self.reference = f'BC-{year}-{num:04d}'
        super().save(*args, **kwargs)


class PurchaseOrderLine(BaseModel):
    """Ligne de commande."""

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('bon de commande')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_lines',
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
    received_quantity = models.IntegerField(_('quantité reçue'), default=0)

    class Meta:
        verbose_name = _('ligne de commande')
        verbose_name_plural = _('lignes de commande')
        unique_together = ['purchase_order', 'product']

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Mise à jour du montant total de la commande
        order = self.purchase_order
        order.total_amount = sum(line.total_price for line in order.lines.all())
        order.save(update_fields=['total_amount'])

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def remaining_quantity(self):
        return self.quantity - self.received_quantity
