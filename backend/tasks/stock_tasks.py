"""
Tâches Celery pour la gestion des stocks.
"""
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(name='tasks.stock_tasks.check_low_stock')
def check_low_stock():
    """Vérifie les stocks bas et envoie des notifications."""
    logger.info('Vérification des stocks bas...')
    # Implémentation à venir
    return 'OK'
