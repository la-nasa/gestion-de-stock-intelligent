"""
Modèles de gestion des catégories et produits.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel, MetaDataModel


class Category(BaseModel):
    """Catégorie de produits."""

    name = models.CharField(_('nom'), max_length=200)
    code = models.CharField(_('code'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('catégorie parente')
    )
    icon = models.CharField(_('icône'), max_length=50, blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    level = models.IntegerField(_('niveau'), default=0, editable=False)
    sort_order = models.IntegerField(_('ordre'), default=0)

    class Meta:
        verbose_name = _('catégorie')
        verbose_name_plural = _('catégories')
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)


class Product(BaseModel):
    """Produit en stock."""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Actif')
        INACTIVE = 'INACTIVE', _('Inactif')
        DISCONTINUED = 'DISCONTINUED', _('Abandonné')
        ON_ORDER = 'ON_ORDER', _('En commande')

    class Unit(models.TextChoices):
        PIECE = 'PIECE', _('Pièce')
        BOX = 'BOX', _('Boîte')
        KG = 'KG', _('Kilogramme')
        LITER = 'LITER', _('Litre')
        METER = 'METER', _('Mètre')
        PACK = 'PACK', _('Pack')
        SET = 'SET', _('Ensemble')

    # Identifiants
    name = models.CharField(_('nom'), max_length=300)
    reference = models.CharField(_('référence'), max_length=100, unique=True, db_index=True)
    barcode = models.CharField(_('code-barres'), max_length=100, unique=True, null=True, blank=True)
    sku = models.CharField(_('SKU'), max_length=100, unique=True, db_index=True)

    # Classification
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('catégorie')
    )
    brand = models.CharField(_('marque'), max_length=200, blank=True)
    model_number = models.CharField(_('numéro de modèle'), max_length=200, blank=True)
    description = models.TextField(_('description'), blank=True)
    specifications = models.JSONField(
        _('spécifications techniques'),
        default=dict,
        blank=True
    )

    # Gestion stock
    unit = models.CharField(
        _('unité'),
        max_length=20,
        choices=Unit.choices,
        default=Unit.PIECE
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    # Prix
    unit_price = models.DecimalField(
        _('prix unitaire'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    currency = models.CharField(_('devise'), max_length=3, default='XAF')

    # Seuils
    min_stock = models.IntegerField(_('stock minimum'), default=0)
    max_stock = models.IntegerField(_('stock maximum'), default=0)
    reorder_point = models.IntegerField(_('point de commande'), default=0)
    optimal_quantity = models.IntegerField(_('quantité optimale'), default=0)

    # Traçabilité
    requires_batch = models.BooleanField(_('nécessite un lot'), default=False)
    requires_expiry = models.BooleanField(_('nécessite une date d\'expiration'), default=False)
    warranty_months = models.IntegerField(_('garantie (mois)'), default=0)
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('fournisseur principal')
    )

    # Médias
    image = models.ImageField(
        _('image'),
        upload_to='products/%Y/%m/',
        blank=True,
        null=True
    )
    datasheet = models.FileField(
        _('fiche technique'),
        upload_to='datasheets/%Y/%m/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('produit')
        verbose_name_plural = _('produits')
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['supplier']),
        ]
        permissions = [
            ("view_product_cost", "Peut voir le coût des produits"),
            ("manage_product", "Peut gérer les produits"),
        ]

    def __str__(self):
        return f"{self.name} ({self.reference})"

    @property
    def total_value(self):
        """Valeur totale du stock pour ce produit."""
        total_qty = sum(
            stock.quantity for stock in self.stocks.filter(is_deleted=False)
        )
        return total_qty * self.unit_price

    @property
    def is_low_stock(self):
        """Vérifie si le stock est bas."""
        total_qty = sum(
            stock.quantity for stock in self.stocks.filter(is_deleted=False)
        )
        return total_qty <= self.min_stock
