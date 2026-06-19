"""
Tâches Celery pour les rapports.
"""
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(name='tasks.report_tasks.generate_daily_reports')
def generate_daily_reports():
    """Génère les rapports quotidiens."""
    logger.info('Génération des rapports quotidiens...')
    return 'OK'
