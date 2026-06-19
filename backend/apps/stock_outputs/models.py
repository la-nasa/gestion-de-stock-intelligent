"""
Modèles pour les sorties de stock.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class StockOutput(BaseModel):
    """Bon de sortie de stock."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Brouillon')
        VALIDATED = 'VALIDATED', _('Validé')
        CANCELLED = 'CANCELLED', _('Annulé')

    class Reason(models.TextChoices):
        INTERNAL_USE = 'INTERNAL_USE', _('Usage interne')
        TRANSFER = 'TRANSFER', _('Transfert')
        DAMAGE = 'DAMAGE', _('Dommage')
        EXPIRED = 'EXPIRED', _('Expiré')
        LOSS = 'LOSS', _('Perte')
        RETURN = 'RETURN', _('Retour fournisseur')
        OTHER = 'OTHER', _('Autre')

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
    reason = models.CharField(
        _('motif'),
        max_length=20,
        choices=Reason.choices,
        default=Reason.INTERNAL_USE
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.PROTECT,
        related_name='stock_outputs',
        verbose_name=_('entrepôt')
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_outputs',
        verbose_name=_('département bénéficiaire')
    )
    recipient = models.CharField(
        _('bénéficiaire'),
        max_length=200,
        blank=True
    )
    output_date = models.DateTimeField(_('date de sortie'), auto_now_add=True)
    issued_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_outputs',
        verbose_name=_('remis par')
    )
    received_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_outputs',
        verbose_name=_('reçu par')
    )
    validated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_outputs',
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
        verbose_name = _('sortie de stock')
        verbose_name_plural = _('sorties de stock')
        ordering = ['-output_date']

    def __str__(self):
        return f"SOR-{self.reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            from django.utils import timezone
            year = timezone.now().year
            last = StockOutput.objects.filter(
                reference__startswith=f'SOR-{year}'
            ).order_by('-reference').first()
            if last:
                num = int(last.reference.split('-')[-1]) + 1
            else:
                num = 1
            self.reference = f'SOR-{year}-{num:04d}'
        super().save(*args, **kwargs)


class StockOutputLine(BaseModel):
    """Ligne de sortie de stock."""

    output = models.ForeignKey(
        StockOutput,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('sortie')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='output_lines',
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

    class Meta:
        verbose_name = _('ligne de sortie')
        verbose_name_plural = _('lignes de sortie')

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
