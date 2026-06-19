"""
Vues pour l'authentification.
"""
import uuid
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.v1.serializers.auth_serializers import (
    LoginSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer,
)
from core.utils.response import success_response, error_response
from apps.accounts.models import RefreshToken, LoginHistory

User = get_user_model()


def get_client_ip(request):
    """Récupère l'adresse IP du client."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Récupère le user agent."""
    return request.META.get('HTTP_USER_AGENT', '')


def create_login_history(user, request, is_successful=True, failure_reason=''):
    """Crée une entrée dans l'historique de connexion."""
    LoginHistory.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        is_successful=is_successful,
        failure_reason=failure_reason
    )


def generate_token_pair(user):
    """Génère une paire de tokens JWT."""
    jwt_token = JWTRefreshToken.for_user(user)
    
    # Stocker le refresh token
    refresh = RefreshToken.objects.create(
        user=user,
        token=str(jwt_token),
        expires_at=timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
    )
    
    return {
        'access_token': str(jwt_token.access_token),
        'refresh_token': str(jwt_token),
        'expires_in': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
        'token_type': 'Bearer',
        'user': UserProfileSerializer(user).data
    }


class LoginView(views.APIView):
    """Vue de connexion."""
    
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response('Connexion réussie'),
            400: "Identifiants invalides",
            401: "Authentification échouée",
            429: "Trop de tentatives"
        },
        operation_description="Authentifie un utilisateur et retourne les tokens JWT."
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return error_response(
                message="Échec de l'authentification",
                errors=serializer.errors,
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user = serializer.validated_data['user']
        
        # Mise à jour des informations de connexion
        user.last_login = timezone.now()
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=['last_login', 'last_login_ip'])
        
        # Historique de connexion
        create_login_history(user, request, is_successful=True)
        
        # Générer les tokens
        tokens = generate_token_pair(user)
        
        return success_response(
            data=tokens,
            message="Connexion réussie",
            status_code=status.HTTP_200_OK
        )


class RegisterView(views.APIView):
    """Vue d'inscription."""
    
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: "Inscription réussie",
            400: "Données invalides"
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message="Échec de l'inscription",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        
        # Générer les tokens directement
        tokens = generate_token_pair(user)
        
        return success_response(
            data=tokens,
            message="Inscription réussie",
            status_code=status.HTTP_201_CREATED
        )


class TokenRefreshView(views.APIView):
    """Vue de rafraîchissement de token."""
    
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        request_body=TokenRefreshSerializer,
        responses={
            200: "Token rafraîchi",
            400: "Token invalide"
        }
    )
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message="Token invalide",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        stored_token = serializer.validated_data['refresh_token']
        
        try:
            # Vérifier le token JWT
            jwt_token = JWTRefreshToken(stored_token.token)
            
            # Révoquer l'ancien token
            stored_token.revoke('Token refreshed')
            
            # Générer une nouvelle paire
            user = stored_token.user
            tokens = generate_token_pair(user)
            
            return success_response(
                data=tokens,
                message="Token rafraîchi avec succès"
            )
        except TokenError:
            return error_response(
                message="Token invalide ou expiré",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(views.APIView):
    """Vue de déconnexion."""
    
    @swagger_auto_schema(
        request_body=TokenRefreshSerializer,
        responses={200: "Déconnexion réussie"}
    )
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if refresh_token:
            try:
                token = RefreshToken.objects.get(token=refresh_token, user=request.user)
                token.revoke('User logout')
            except RefreshToken.DoesNotExist:
                pass
        
        return success_response(
            message="Déconnexion réussie"
        )


class ChangePasswordView(views.APIView):
    """Vue de changement de mot de passe."""
    
    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: "Mot de passe changé",
            400: "Erreur de validation"
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return error_response(
                message="Erreur de validation",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return success_response(
            message="Mot de passe changé avec succès. Veuillez vous reconnecter."
        )


class PasswordResetRequestView(views.APIView):
    """Vue de demande de réinitialisation de mot de passe."""
    
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        request_body=PasswordResetRequestSerializer,
        responses={200: "Email envoyé"}
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message="Erreur de validation",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Logique d'envoi d'email à implémenter
        # Pour l'instant, on retourne toujours un succès pour éviter
        # de révéler si l'email existe
        
        return success_response(
            message="Si un compte existe avec cet email, vous recevrez les instructions."
        )


class PasswordResetConfirmView(views.APIView):
    """Vue de confirmation de réinitialisation."""
    
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        request_body=PasswordResetConfirmSerializer,
        responses={200: "Mot de passe réinitialisé"}
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message="Erreur de validation",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(
            message="Mot de passe réinitialisé avec succès."
        )


class ProfileView(views.APIView):
    """Vue du profil utilisateur."""
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return success_response(data=serializer.data)
    
    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={200: "Profil mis à jour"}
    )
    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return error_response(
                message="Erreur de validation",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return success_response(
            data=serializer.data,
            message="Profil mis à jour"
        )


class SessionListView(views.APIView):
    """Vue des sessions actives."""
    
    def get(self, request):
        sessions = RefreshToken.objects.filter(
            user=request.user,
            is_revoked=False,
            expires_at__gt=timezone.now()
        )
        
        data = [{
            'id': str(session.id),
            'created_at': session.created_at,
            'expires_at': session.expires_at,
            'is_current': session.token == request.auth.token.decode() if hasattr(request.auth, 'token') else False
        } for session in sessions]
        
        return success_response(data=data)


class SessionRevokeView(views.APIView):
    """Vue de révocation de session."""
    
    def post(self, request, session_id):
        try:
            session = RefreshToken.objects.get(
                id=session_id,
                user=request.user
            )
            session.revoke('Manually revoked')
            return success_response(message="Session révoquée")
        except RefreshToken.DoesNotExist:
            return error_response(
                message="Session introuvable",
                status_code=status.HTTP_404_NOT_FOUND
            )
