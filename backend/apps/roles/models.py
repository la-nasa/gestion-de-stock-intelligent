"""
Modèles de gestion des rôles et permissions.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel, AuditModel


class Role(BaseModel):
    """Définition des rôles."""

    name = models.CharField(_('nom'), max_length=100, unique=True)
    code = models.CharField(_('code'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True)
    is_system = models.BooleanField(_('rôle système'), default=False)
    is_active = models.BooleanField(_('actif'), default=True)
    level = models.IntegerField(_('niveau hiérarchique'), default=0)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('rôle parent')
    )

    class Meta:
        verbose_name = _('rôle')
        verbose_name_plural = _('rôles')
        ordering = ['level', 'name']
        permissions = [
            ("manage_roles", "Peut gérer les rôles"),
        ]

    def __str__(self):
        return self.name


class Permission(BaseModel):
    """Permissions granulaires."""

    class Scope(models.TextChoices):
        GLOBAL = 'GLOBAL', _('Global')
        CAMPUS = 'CAMPUS', _('Campus')
        DEPARTMENT = 'DEPARTMENT', _('Département')
        WAREHOUSE = 'WAREHOUSE', _('Entrepôt')
        PERSONAL = 'PERSONAL', _('Personnel')

    code = models.CharField(_('code'), max_length=200, unique=True)
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    module = models.CharField(_('module'), max_length=100)
    scope = models.CharField(
        _('portée'),
        max_length=20,
        choices=Scope.choices,
        default=Scope.GLOBAL
    )
    is_active = models.BooleanField(_('actif'), default=True)

    class Meta:
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        ordering = ['module', 'code']

    def __str__(self):
        return f"{self.module}.{self.code}"


class RolePermission(BaseModel):
    """Association rôle-permission."""

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name=_('rôle')
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name=_('permission')
    )
    granted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('accordée par')
    )

    class Meta:
        verbose_name = _('permission de rôle')
        verbose_name_plural = _('permissions de rôle')
        unique_together = ['role', 'permission']

    def __str__(self):
        return f"{self.role.name} → {self.permission.code}"
