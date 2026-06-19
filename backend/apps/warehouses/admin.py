from django.contrib import admin
from .models import Warehouse

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'campus', 'type', 'status', 'manager']
    list_filter = ['type', 'status', 'campus']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
