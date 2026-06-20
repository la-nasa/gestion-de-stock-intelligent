from django.db import models
from core.models.base import BaseModel

class Product(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Actif"
        INACTIVE = "INACTIVE", "Inactif"
        DISCONTINUED = "DISCONTINUED", "Abandonné"
    class Unit(models.TextChoices):
        PIECE = "PIECE", "Pièce"
        BOX = "BOX", "Boîte"
        KG = "KG", "Kilogramme"
        LITER = "LITER", "Litre"
        METER = "METER", "Mètre"
        PACK = "PACK", "Pack"
        SET = "SET", "Ensemble"

    name = models.CharField(max_length=300)
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    category = models.ForeignKey("categories.Category", on_delete=models.PROTECT, related_name="products")
    brand = models.CharField(max_length=200, blank=True)
    model_number = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="XAF")
    min_stock = models.IntegerField(default=0)
    max_stock = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=0)
    optimal_quantity = models.IntegerField(default=0)
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    datasheet = models.FileField(upload_to="datasheets/", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["reference"]), models.Index(fields=["sku"])]

    def __str__(self): return f"{self.name} ({self.reference})"
    @property
    def total_value(self):
        from apps.stock_movements.models import Stock
        total = Stock.objects.filter(product=self, is_deleted=False).aggregate(t=models.Sum(models.F("quantity") * models.F("unit_price")))["t"]
        return total or 0
    @property
    def is_low_stock(self):
        from apps.stock_movements.models import Stock
        total = Stock.objects.filter(product=self, is_deleted=False).aggregate(t=models.Sum("quantity"))["t"] or 0
        return total <= self.min_stock