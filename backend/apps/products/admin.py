from django.contrib import admin
from .models import Product
from apps.categories.models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "parent", "level", "is_active"]
    search_fields = ["name", "code"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "reference", "category", "unit_price", "status"]
    search_fields = ["name", "reference", "sku"]
    list_filter = ["status", "category"]
