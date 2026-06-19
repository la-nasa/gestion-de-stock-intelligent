"""
Serializers pour l'authentification.
"""
import re
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers
from apps.accounts.models import User, LoginHistory, RefreshToken


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion."""
    
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': "L'email est obligatoire.",
            'invalid': "Format d'email invalide."
        }
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': "Le mot de passe est obligatoire."
        }
    )
    remember_me = serializers.BooleanField(default=False)
    
    def validate_email(self, value):
        """Valide et normalise l'email."""
        value = value.lower().strip()
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Format d'email invalide.")
        return value
    
    def validate(self, attrs):
        """Authentifie l'utilisateur."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Vérifier que l'utilisateur existe
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': "Aucun compte trouvé avec cet email."
            })
        
        # Vérifier si le compte est actif
        if not user.is_active:
            raise serializers.ValidationError({
                'email': "Ce compte a été désactivé. Contactez l'administrateur."
            })
        
        # Vérifier le nombre de tentatives
        if user.login_attempts >= 5:
            raise serializers.ValidationError({
                'email': "Compte temporairement bloqué. Veuillez réessayer dans 30 minutes."
            })
        
        # Authentifier
        user = authenticate(request=self.context.get('request'), email=email, password=password)
        
        if not user:
            # Incrémenter les tentatives échouées
            try:
                failed_user = User.objects.get(email=email)
                failed_user.increment_login_attempts()
            except User.DoesNotExist:
                pass
            
            raise serializers.ValidationError({
                'password': "Email ou mot de passe incorrect."
            })
        
        # Réinitialiser les tentatives
        user.reset_login_attempts()
        
        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        error_messages={
            'min_length': "Le mot de passe doit contenir au moins 8 caractères."
        }
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'matricule',
            'password', 'password_confirm', 'phone', 'department'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'matricule': {'required': True},
        }
    
    def validate_email(self, value):
        """Valide l'unicité de l'email."""
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value
    
    def validate_matricule(self, value):
        """Valide le format et l'unicité du matricule."""
        value = value.upper().strip()
        if not re.match(r'^[A-Z0-9]{3,20}$', value):
            raise serializers.ValidationError(
                "Le matricule doit contenir 3 à 20 caractères alphanumériques."
            )
        if User.objects.filter(matricule=value).exists():
            raise serializers.ValidationError("Ce matricule est déjà utilisé.")
        return value
    
    def validate_password(self, value):
        """Valide la force du mot de passe."""
        validate_password(value)
        if len(value) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une minuscule.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")
        return value
    
    def validate(self, attrs):
        """Vérifie la correspondance des mots de passe."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': "Les mots de passe ne correspondent pas."
            })
        return attrs
    
    def create(self, validated_data):
        """Crée un nouvel utilisateur."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer pour le rafraîchissement de token."""
    
    refresh_token = serializers.CharField(required=True)
    
    def validate_refresh_token(self, value):
        """Valide le refresh token."""
        try:
            token = RefreshToken.objects.get(token=value)
            if not token.is_valid:
                raise serializers.ValidationError("Token invalide ou expiré.")
            if token.is_revoked:
                raise serializers.ValidationError("Token révoqué.")
            return token
        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError("Token invalide.")


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe."""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        min_length=8
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Vérifie l'ancien mot de passe."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value
    
    def validate_new_password(self, value):
        """Valide le nouveau mot de passe."""
        validate_password(value)
        return value
    
    def validate(self, attrs):
        """Vérifie la correspondance."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Les mots de passe ne correspondent pas."
            })
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({
                'new_password': "Le nouveau mot de passe doit être différent de l'ancien."
            })
        return attrs
    
    def save(self):
        """Change le mot de passe."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.password_changed_at = timezone.now()
        user.save()
        # Révoquer tous les refresh tokens
        user.refresh_tokens.update(is_revoked=True, revoked_at=timezone.now())
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer pour la demande de réinitialisation."""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        value = value.lower().strip()
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError(
                "Aucun compte actif trouvé avec cet email."
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer pour la confirmation de réinitialisation."""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Les mots de passe ne correspondent pas."
            })
        return attrs


class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer pour la configuration 2FA."""
    pass


class TwoFactorVerifySerializer(serializers.Serializer):
    """Serializer pour la vérification 2FA."""
    code = serializers.CharField(required=True, min_length=6, max_length=6)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur."""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    campus_name = serializers.CharField(source='campus.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'matricule', 'first_name', 'last_name',
            'full_name', 'phone', 'avatar', 'role',
            'department', 'department_name',
            'campus', 'campus_name',
            'is_active', 'is_verified', 'email_verified',
            'two_factor_enabled', 'last_login',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email', 'matricule', 'role',
            'is_active', 'is_verified', 'email_verified',
            'two_factor_enabled', 'last_login',
            'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
