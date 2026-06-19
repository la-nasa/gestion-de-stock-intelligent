# Pour le déploiement, toujours utiliser les settings de production
# Les settings de développement sont utilisés uniquement en local
import os

if os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings.production':
    from .production import *
elif os.environ.get('RENDER') == 'true':
    from .production import *
else:
    try:
        from .development import *
    except ImportError:
        from .production import *