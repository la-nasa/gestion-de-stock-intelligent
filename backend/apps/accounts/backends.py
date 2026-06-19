"""
Backends d'authentification personnalisés.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrMatriculeBackend(ModelBackend):
    """
    Backend permettant l'authentification par email OU matricule.
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return None
        
        try:
            # Recherche par email ou matricule
            user = User.objects.get(
                Q(email=email) | Q(matricule=email)
            )
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def user_can_authenticate(self, user):
        """Vérifie si l'utilisateur peut s'authentifier."""
        return user.is_active and not user.is_deleted
