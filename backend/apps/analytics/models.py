"""
Modèles pour les analytics et statistiques.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel


class DailyStockSnapshot(BaseModel):
    """Snapshot quotidien des stocks."""

    date = models.DateField(_('date'), db_index=True)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='daily_snapshots',
        verbose_name=_('produit')
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.CASCADE,
        related_name='daily_snapshots',
        verbose_name=_('entrepôt')
    )
    quantity = models.IntegerField(_('quantité'))
    reserved_quantity = models.IntegerField(_('quantité réservée'))
    unit_price = models.DecimalField(
        _('prix unitaire'),
        max_digits=15,
        decimal_places=2
    )
    total_value = models.DecimalField(
        _('valeur totale'),
        max_digits=15,
        decimal_places=2
    )
    movements_in = models.IntegerField(_('entrées'), default=0)
    movements_out = models.IntegerField(_('sorties'), default=0)

    class Meta:
        verbose_name = _('snapshot stock')
        verbose_name_plural = _('snapshots stock')
        unique_together = ['date', 'product', 'warehouse']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['product', '-date']),
        ]

    def __str__(self):
        return f"{self.date} - {self.product.name}: {self.quantity}"


class MonthlyConsumption(BaseModel):
    """Consommation mensuelle par produit."""

    year = models.IntegerField(_('année'))
    month = models.IntegerField(_('mois'))
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='monthly_consumption',
        verbose_name=_('produit')
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='monthly_consumption',
        verbose_name=_('département')
    )
    quantity_consumed = models.IntegerField(_('quantité consommée'))
    total_cost = models.DecimalField(
        _('coût total'),
        max_digits=15,
        decimal_places=2
    )

    class Meta:
        verbose_name = _('consommation mensuelle')
        verbose_name_plural = _('consommations mensuelles')
        unique_together = ['year', 'month', 'product', 'department']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.month:02d}/{self.year} - {self.product.name}"


class KPI(models.Model):
    """Indicateur clé de performance."""

    name = models.CharField(_('nom'), max_length=200)
    code = models.CharField(_('code'), max_length=100, unique=True)
    value = models.DecimalField(
        _('valeur'),
        max_digits=20,
        decimal_places=4,
        default=0
    )
    unit = models.CharField(_('unité'), max_length=50, blank=True)
    target = models.DecimalField(
        _('objectif'),
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True
    )
    trend = models.DecimalField(
        _('tendance (%)'),
        max_digits=8,
        decimal_places=2,
        default=0
    )
    calculated_at = models.DateTimeField(_('calculé le'), auto_now=True)
    period = models.CharField(
        _('période'),
        max_length=20,
        choices=[
            ('DAILY', 'Journalier'),
            ('WEEKLY', 'Hebdomadaire'),
            ('MONTHLY', 'Mensuel'),
            ('YEARLY', 'Annuel'),
        ],
        default='MONTHLY'
    )

    class Meta:
        verbose_name = _('KPI')
        verbose_name_plural = _('KPIs')
        ordering = ['name']

    def __str__(self):
        return f"{self.name}: {self.value} {self.unit}"
