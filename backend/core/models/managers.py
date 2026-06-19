"""
Managers optimisés pour les modèles Django.
"""
from django.db import models
from django.db.models import QuerySet


class OptimizedQuerySet(QuerySet):
    """QuerySet avec méthodes d'optimisation."""
    
    def with_select_related(self, *fields):
        """Ajoute automatiquement select_related."""
        if fields:
            return self.select_related(*fields)
        return self
    
    def with_prefetch_related(self, *fields):
        """Ajoute automatiquement prefetch_related."""
        if fields:
            return self.prefetch_related(*fields)
        return self
    
    def active(self):
        """Filtre les enregistrements actifs."""
        return self.filter(is_deleted=False)
    
    def recent(self, days: int = 30):
        """Filtre les enregistrements récents."""
        from django.utils import timezone
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)


class OptimizedManager(models.Manager):
    """Manager avec méthodes d'optimisation."""
    
    def get_queryset(self):
        return OptimizedQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def recent(self, days: int = 30):
        return self.get_queryset().recent(days)


class CacheManager:
    """Gestionnaire de cache pour les requêtes fréquentes."""
    
    @staticmethod
    def cache_key(model_name: str, identifier: str) -> str:
        """Génère une clé de cache."""
        return f'model:{model_name}:{identifier}'
    
    @staticmethod
    def get_cached(model_class, identifier, timeout=300):
        """Récupère un objet du cache ou de la base."""
        from django.core.cache import cache
        
        key = CacheManager.cache_key(model_class.__name__, str(identifier))
        obj = cache.get(key)
        
        if obj is None:
            try:
                obj = model_class.objects.get(id=identifier)
                cache.set(key, obj, timeout)
            except model_class.DoesNotExist:
                return None
        
        return obj
    
    @staticmethod
    def invalidate(model_class, identifier):
        """Invalide le cache pour un objet."""
        from django.core.cache import cache
        key = CacheManager.cache_key(model_class.__name__, str(identifier))
        cache.delete(key)
    
    @staticmethod
    def invalidate_pattern(pattern: str):
        """Invalide toutes les clés correspondant au pattern."""
        from django_redis import get_redis_connection
        redis = get_redis_connection('default')
        keys = redis.keys(f'*{pattern}*')
        if keys:
            redis.delete(*keys)