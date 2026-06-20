from django.db import models
from core.models.base import BaseModel

class Category(BaseModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    level = models.IntegerField(default=0)
    sort_order = models.IntegerField(default=0)
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["sort_order", "name"]
    def __str__(self): return self.name
    def save(self, *args, **kwargs):
        if self.parent: self.level = self.parent.level + 1
        else: self.level = 0
        super().save(*args, **kwargs)