from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_person', 'email', 'status', 'rating']
    list_filter = ['status', 'country']
    search_fields = ['name', 'code', 'email', 'contact_person']
    readonly_fields = ['created_at', 'updated_at']
