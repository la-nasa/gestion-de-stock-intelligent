from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'level', 'is_active']
    list_filter = ['is_active', 'level']
    search_fields = ['name', 'code']
    prepopulated_fields = {'code': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'reference', 'category', 'unit_price', 'status']
    list_filter = ['status', 'category', 'unit']
    search_fields = ['name', 'reference', 'sku', 'barcode']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Identifiants', {'fields': ('name', 'reference', 'sku', 'barcode')}),
        ('Classification', {'fields': ('category', 'brand', 'model_number', 'unit')}),
        ('Prix', {'fields': ('unit_price', 'currency')}),
        ('Gestion stock', {'fields': ('min_stock', 'max_stock', 'reorder_point', 'optimal_quantity')}),
        ('Statut', {'fields': ('status', 'is_deleted')}),
    )
