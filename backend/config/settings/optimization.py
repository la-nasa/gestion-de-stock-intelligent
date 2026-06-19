"""
Paramètres d'optimisation pour Django.
À importer dans les settings de production.
"""
from .base import *  # noqa

# Cache avec Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_CACHE_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 100,
                'timeout': 30,
            },
            'MAX_CONNECTIONS': 1000,
            'PICKLE_VERSION': -1,
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.lz4.Lz4Compressor',
        },
        'KEY_PREFIX': 'iuc_optimized',
        'TIMEOUT': 300,  # 5 minutes par défaut
    }
}

# Session avec cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# Compression des fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware d'optimisation
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # Au début
    'django.middleware.gzip.GZipMiddleware',
] + MIDDLEWARE + [
    'django.middleware.cache.FetchFromCacheMiddleware',  # À la fin
]

# Cache des templates
TEMPLATES[0]['OPTIONS']['loaders'] = [  # noqa
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Optimisation base de données
DATABASES['default']['OPTIONS'] = {  # noqa
    'pool': True,
    'pool_size': 20,
    'max_overflow': 40,
    'pool_timeout': 30,
    'pool_recycle': 3600,
}

# Désactiver le debug toolbar en production
DEBUG = False

# Désactiver les middlewares inutiles en production
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in [
    m.split('.')[-1] for m in MIDDLEWARE
]:
    MIDDLEWARE = [
        m for m in MIDDLEWARE
        if 'DebugToolbar' not in m
    ]