"""
URLs d'authentification.
"""
from django.urls import path
from api.v1.views.auth_views import (
    LoginView,
    RegisterView,
    TokenRefreshView,
    LogoutView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ProfileView,
    SessionListView,
    SessionRevokeView,
)

urlpatterns = [
    # Authentification
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    
    # Mot de passe
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    
    # Profil
    path('auth/profile/', ProfileView.as_view(), name='auth-profile'),
    
    # Sessions
    path('auth/sessions/', SessionListView.as_view(), name='auth-sessions'),
    path('auth/sessions/<uuid:session_id>/revoke/', SessionRevokeView.as_view(), name='auth-session-revoke'),
]
