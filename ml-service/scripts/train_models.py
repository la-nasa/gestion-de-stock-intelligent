"""
Script d'entraînement des modèles de prévision.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from app.services.forecasting_service import forecasting_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_training_data(days: int = 365) -> pd.DataFrame:
    """Génère des données d'entraînement simulées."""
    base_date = datetime.now() - timedelta(days=days)
    
    dates = [base_date + timedelta(days=i) for i in range(days)]
    
    # Créer une tendance avec saisonnalité
    trend = np.linspace(100, 200, days)
    weekly = 20 * np.sin(2 * np.pi * np.arange(days) / 7)
    monthly = 30 * np.sin(2 * np.pi * np.arange(days) / 30)
    noise = np.random.normal(0, 15, days)
    
    quantities = trend + weekly + monthly + noise
    quantities = np.maximum(quantities, 0)
    
    return pd.DataFrame({
        'date': dates,
        'quantity': quantities,
    })


def main():
    """Fonction principale d'entraînement."""
    logger.info("=" * 50)
    logger.info("Entraînement des modèles de prévision")
    logger.info("=" * 50)
    
    # Générer les données
    logger.info("Génération des données d'entraînement...")
    data = generate_training_data(365)
    logger.info(f"  {len(data)} points de données générés")
    
    # Entraîner chaque modèle
    models = ['prophet', 'xgboost']  # LSTM nécessite GPU
    
    for model_name in models:
        try:
            logger.info(f"\nEntraînement de {model_name}...")
            result = forecasting_service.train_model(model_name, data)
            
            logger.info(f"  ✓ {model_name} entraîné avec succès")
            logger.info(f"    MAE:  {result['metrics'].get('mae', 'N/A')}")
            logger.info(f"    RMSE: {result['metrics'].get('rmse', 'N/A')}")
        except Exception as e:
            logger.error(f"  ✗ Erreur {model_name}: {e}")
    
    # Comparer les modèles
    logger.info("\nComparaison des modèles...")
    comparison = forecasting_service.compare_models(data, 30)
    
    logger.info(f"  Meilleur modèle: {comparison['best_model']}")
    logger.info(f"  Meilleur MAE: {comparison['best_mae']}")
    
    for name, result in comparison['results'].items():
        status = '✓' if result['status'] == 'success' else '✗'
        metrics = result.get('metrics', {})
        logger.info(f"  {status} {name}: MAE={metrics.get('mae', 'N/A'):.2f}")
    
    logger.info("\n✓ Entraînement terminé !")


if __name__ == '__main__':
    main()