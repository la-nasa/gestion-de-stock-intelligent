"""
Configuration de l'interface d'administration Django.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User, LoginHistory, RefreshToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuration admin pour le modèle User."""
    
    list_display = [
        'email', 'matricule', 'first_name', 'last_name',
        'role', 'department', 'is_active', 'is_verified',
        'last_login'
    ]
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_verified',
        'department', 'campus'
    ]
    search_fields = [
        'email', 'matricule', 'first_name', 'last_name',
        'phone'
    ]
    ordering = ['-created_at']
    readonly_fields = ['last_login', 'last_login_ip', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Identifiants'), {
            'fields': ('email', 'username', 'matricule', 'password')
        }),
        (_('Informations personnelles'), {
            'fields': ('first_name', 'last_name', 'phone', 'avatar')
        }),
        (_('Organisation'), {
            'fields': ('department', 'campus', 'role')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'is_verified', 'email_verified',
                'groups', 'user_permissions'
            )
        }),
        (_('Sécurité'), {
            'fields': (
                'two_factor_enabled',
                'last_login', 'last_login_ip',
                'login_attempts', 'password_changed_at'
            )
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'matricule', 'first_name', 'last_name',
                'password1', 'password2', 'role'
            ),
        }),
    )


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'is_successful', 'created_at']
    list_filter = ['is_successful', 'created_at']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = ['created_at']


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'expires_at', 'is_revoked', 'created_at']
    list_filter = ['is_revoked']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'token']


# Configuration du site d'administration
admin.site.site_header = _('IUC Inventory System - Administration')
admin.site.site_title = _('IUC Inventory Admin')
admin.site.index_title = _('Gestion de Stock Intelligente')
admin.site.site_url = '/swagger/'
