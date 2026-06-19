"""
Tâches de nettoyage.
"""
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(name='tasks.cleanup_tasks.cleanup_old_sessions')
def cleanup_old_sessions():
    """Nettoie les anciennes sessions."""
    logger.info('Nettoyage des anciennes sessions...')
    return 'OK'
