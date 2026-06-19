"""
Modèles de gestion des comptes utilisateurs.
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("L'adresse email est obligatoire"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Le superuser doit avoir is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Le superuser doit avoir is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """Modèle utilisateur personnalisé."""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        MANAGER = 'MANAGER', _('Gestionnaire')
        SUPERVISOR = 'SUPERVISOR', _('Superviseur')
        OPERATOR = 'OPERATOR', _('Opérateur')
        VIEWER = 'VIEWER', _('Lecteur')
        AUDITOR = 'AUDITOR', _('Auditeur')

    # Identifiants
    email = models.EmailField(
        _('adresse email'),
        unique=True,
        db_index=True,
        error_messages={
            'unique': _("Un utilisateur avec cet email existe déjà."),
        }
    )
    username = models.CharField(
        _('nom d\'utilisateur'),
        max_length=150,
        unique=True,
        db_index=True,
        null=True,
        blank=True
    )
    matricule = models.CharField(
        _('matricule'),
        max_length=50,
        unique=True,
        db_index=True
    )

    # Informations personnelles
    first_name = models.CharField(_('prénom'), max_length=150)
    last_name = models.CharField(_('nom'), max_length=150)
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True
    )

    # Rôle et permissions
    role = models.CharField(
        _('rôle'),
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER
    )

    # Statut
    is_active = models.BooleanField(_('actif'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_verified = models.BooleanField(_('vérifié'), default=False)
    email_verified = models.BooleanField(_('email vérifié'), default=False)

    # Sécurité
    last_login = models.DateTimeField(_('dernière connexion'), null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(
        _('IP dernière connexion'),
        null=True,
        blank=True
    )
    login_attempts = models.IntegerField(_('tentatives de connexion'), default=0)
    password_changed_at = models.DateTimeField(
        _('mot de passe changé le'),
        null=True,
        blank=True
    )

    # 2FA
    two_factor_enabled = models.BooleanField(_('2FA activé'), default=False)
    two_factor_secret = models.CharField(
        _('secret 2FA'),
        max_length=255,
        blank=True
    )

    # Relations
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('département')
    )
    campus = models.ForeignKey(
        'campuses.Campus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('campus')
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'matricule']

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['matricule']),
            models.Index(fields=['role']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active']),
        ]
        permissions = [
            ("view_all_users", "Peut voir tous les utilisateurs"),
            ("manage_users", "Peut gérer les utilisateurs"),
            ("export_users", "Peut exporter la liste des utilisateurs"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.matricule})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def increment_login_attempts(self):
        self.login_attempts += 1
        self.save(update_fields=['login_attempts'])

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.save(update_fields=['login_attempts'])

    def has_role(self, role):
        return self.role == role

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_manager(self):
        return self.role in [self.Role.ADMIN, self.Role.MANAGER]


class LoginHistory(BaseModel):
    """Historique des connexions utilisateur."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history',
        verbose_name=_('utilisateur')
    )
    ip_address = models.GenericIPAddressField(_('adresse IP'))
    user_agent = models.TextField(_('user agent'), blank=True)
    location = models.CharField(_('localisation'), max_length=255, blank=True)
    is_successful = models.BooleanField(_('connexion réussie'), default=True)
    failure_reason = models.CharField(
        _('raison de l\'échec'),
        max_length=255,
        blank=True
    )

    class Meta:
        verbose_name = _('historique de connexion')
        verbose_name_plural = _('historiques de connexion')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        status = '✓' if self.is_successful else '✗'
        return f"{self.user} - {status} - {self.ip_address}"


class RefreshToken(BaseModel):
    """Gestion des refresh tokens."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='refresh_tokens',
        verbose_name=_('utilisateur')
    )
    token = models.CharField(_('token'), max_length=500, unique=True, db_index=True)
    expires_at = models.DateTimeField(_('expire le'))
    is_revoked = models.BooleanField(_('révoqué'), default=False)
    revoked_at = models.DateTimeField(_('révoqué le'), null=True, blank=True)
    revoked_reason = models.CharField(
        _('raison de révocation'),
        max_length=255,
        blank=True
    )

    class Meta:
        verbose_name = _('refresh token')
        verbose_name_plural = _('refresh tokens')
        ordering = ['-created_at']

    def revoke(self, reason=''):
        self.is_revoked = True
        self.revoked_at = timezone.now()
        self.revoked_reason = reason
        self.save(update_fields=['is_revoked', 'revoked_at', 'revoked_reason'])

    @property
    def is_valid(self):
        return not self.is_revoked and self.expires_at > timezone.now()
