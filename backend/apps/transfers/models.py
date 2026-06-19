"""
Modèles de gestion des transferts.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class Transfer(BaseModel):
    """Transfert de stock entre entrepôts."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Brouillon')
        PENDING = 'PENDING', _('En attente')
        APPROVED = 'APPROVED', _('Approuvé')
        IN_TRANSIT = 'IN_TRANSIT', _('En transit')
        COMPLETED = 'COMPLETED', _('Terminé')
        CANCELLED = 'CANCELLED', _('Annulé')
        REJECTED = 'REJECTED', _('Rejeté')

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
    source_warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.PROTECT,
        related_name='outgoing_transfers',
        verbose_name=_('entrepôt source')
    )
    destination_warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.PROTECT,
        related_name='incoming_transfers',
        verbose_name=_('entrepôt destination')
    )
    requested_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='requested_transfers',
        verbose_name=_('demandé par')
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_transfers',
        verbose_name=_('approuvé par')
    )
    approved_at = models.DateTimeField(_('approuvé le'), null=True, blank=True)
    shipped_at = models.DateTimeField(_('expédié le'), null=True, blank=True)
    received_at = models.DateTimeField(_('reçu le'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    total_items = models.IntegerField(_('nombre total d\'articles'), default=0)

    class Meta:
        verbose_name = _('transfert')
        verbose_name_plural = _('transferts')
        ordering = ['-created_at']
        permissions = [
            ("approve_transfer", "Peut approuver un transfert"),
            ("ship_transfer", "Peut expédier un transfert"),
            ("receive_transfer", "Peut recevoir un transfert"),
        ]

    def __str__(self):
        return f"TRF-{self.reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            from django.utils import timezone
            year = timezone.now().year
            last = Transfer.objects.filter(
                reference__startswith=f'TRF-{year}'
            ).order_by('-reference').first()
            if last:
                num = int(last.reference.split('-')[-1]) + 1
            else:
                num = 1
            self.reference = f'TRF-{year}-{num:04d}'
        super().save(*args, **kwargs)


class TransferLine(BaseModel):
    """Ligne de transfert."""

    transfer = models.ForeignKey(
        Transfer,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('transfert')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='transfer_lines',
        verbose_name=_('produit')
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
    source_location = models.CharField(
        _('emplacement source'),
        max_length=100,
        blank=True
    )
    destination_location = models.CharField(
        _('emplacement destination'),
        max_length=100,
        blank=True
    )
    notes = models.TextField(_('notes'), blank=True)

    class Meta:
        verbose_name = _('ligne de transfert')
        verbose_name_plural = _('lignes de transfert')
        unique_together = ['transfer', 'product']

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Mise à jour compteur transfert
        self.transfer.total_items = sum(
            line.quantity for line in self.transfer.lines.all()
        )
        self.transfer.save(update_fields=['total_items'])

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
