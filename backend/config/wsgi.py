import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Appliquer les migrations automatiquement au démarrage
try:
    import django
    django.setup()
    from django.core.management import call_command
    call_command('migrate', '--noinput', verbosity=0)
    print("✓ Migrations appliquées avec succès")
except Exception as e:
    print(f"⚠ Erreur migrations: {e}")

application = get_wsgi_application()