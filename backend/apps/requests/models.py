"""
Modèles de gestion des demandes internes.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class InternalRequest(BaseModel):
    """Demande interne de matériel."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Brouillon')
        SUBMITTED = 'SUBMITTED', _('Soumise')
        APPROVED = 'APPROVED', _('Approuvée')
        PROCESSING = 'PROCESSING', _('En cours')
        DELIVERED = 'DELIVERED', _('Livrée')
        PARTIALLY_DELIVERED = 'PARTIALLY_DELIVERED', _('Partiellement livrée')
        CANCELLED = 'CANCELLED', _('Annulée')
        REJECTED = 'REJECTED', _('Rejetée')

    class Priority(models.TextChoices):
        LOW = 'LOW', _('Basse')
        MEDIUM = 'MEDIUM', _('Moyenne')
        HIGH = 'HIGH', _('Haute')
        URGENT = 'URGENT', _('Urgente')

    reference = models.CharField(
        _('référence'),
        max_length=50,
        unique=True,
        db_index=True
    )
    status = models.CharField(
        _('statut'),
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT
    )
    priority = models.CharField(
        _('priorité'),
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    requester = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_requests',
        verbose_name=_('demandeur')
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.PROTECT,
        related_name='requests',
        verbose_name=_('département')
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.PROTECT,
        related_name='requests',
        verbose_name=_('entrepôt')
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests',
        verbose_name=_('approuvé par')
    )
    approved_at = models.DateTimeField(_('approuvé le'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('livré le'), null=True, blank=True)
    justification = models.TextField(_('justification'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    total_items = models.IntegerField(_('nombre d\'articles'), default=0)

    class Meta:
        verbose_name = _('demande interne')
        verbose_name_plural = _('demandes internes')
        ordering = ['-created_at']
        permissions = [
            ("approve_request", "Peut approuver une demande"),
        ]

    def __str__(self):
        return f"DI-{self.reference} - {self.requester}"

    def save(self, *args, **kwargs):
        if not self.reference:
            from django.utils import timezone
            year = timezone.now().year
            last = InternalRequest.objects.filter(
                reference__startswith=f'DI-{year}'
            ).order_by('-reference').first()
            if last:
                num = int(last.reference.split('-')[-1]) + 1
            else:
                num = 1
            self.reference = f'DI-{year}-{num:04d}'
        super().save(*args, **kwargs)


class InternalRequestLine(BaseModel):
    """Ligne de demande interne."""

    request = models.ForeignKey(
        InternalRequest,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('demande')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='request_lines',
        verbose_name=_('produit')
    )
    quantity = models.IntegerField(_('quantité demandée'))
    delivered_quantity = models.IntegerField(_('quantité livrée'), default=0)
    unit_price = models.DecimalField(
        _('prix unitaire estimé'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('notes'), blank=True)

    class Meta:
        verbose_name = _('ligne de demande')
        verbose_name_plural = _('lignes de demande')
        unique_together = ['request', 'product']

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def remaining_quantity(self):
        return self.quantity - self.delivered_quantity
