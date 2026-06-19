from .base import *

# Development Settings
DEBUG = True
ALLOWED_HOSTS = ['*']

# Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable password validators in development
AUTH_PASSWORD_VALIDATORS = []

# Django Silk for profiling
INSTALLED_APPS += ['silk']
MIDDLEWARE = ['silk.middleware.SilkyMiddleware'] + MIDDLEWARE

# CORS Settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Celery tasks in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Logging for development
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['django.db.backends']['level'] = 'WARNING'

# Disable security settings in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
