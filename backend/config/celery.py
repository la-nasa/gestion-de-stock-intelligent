"""
Configuration Celery pour IUC Inventory System.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('iuc_inventory')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-low-stock-every-hour': {
        'task': 'tasks.stock_tasks.check_low_stock',
        'schedule': crontab(minute=0, hour='*'),
    },
    'generate-daily-reports': {
        'task': 'tasks.report_tasks.generate_daily_reports',
        'schedule': crontab(minute=0, hour=6),
    },
    'cleanup-old-sessions': {
        'task': 'tasks.cleanup_tasks.cleanup_old_sessions',
        'schedule': crontab(minute=0, hour=0),
    },
}
