"""Routes de détection d'anomalies avec vrais modèles."""
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.services.anomaly_service import anomaly_service

router = APIRouter()


class AnomalyDetectionRequest(BaseModel):
    """Requête de détection d'anomalies."""
    product_ids: Optional[List[str]] = None
    warehouse_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sensitivity: float = 0.5
    model: str = "isolation_forest"


class TrainAnomalyRequest(BaseModel):
    """Requête d'entraînement."""
    model: str = "isolation_forest"
    historical_data: List[Dict[str, Any]]
    contamination: float = 0.1


@router.post("/detect")
async def detect_anomalies(request: AnomalyDetectionRequest):
    """Détecte les anomalies dans les données."""
    try:
        # Récupérer les données (simulées ou depuis la DB)
        data = _get_mock_stock_data(90)
        df = pd.DataFrame(data)
        
        # Détection
        result = anomaly_service.detect_anomalies(request.model, df)
        
        # Enrichir avec des informations contextuelles
        for anomaly in result['anomalies']:
            anomaly['context'] = _get_anomaly_context(anomaly)
            anomaly['recommended_action'] = _get_recommended_action(anomaly)
        
        return {
            'status': 'success',
            'detection': result,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train_detector(request: TrainAnomalyRequest):
    """Entraîne un détecteur d'anomalies."""
    try:
        if not request.historical_data:
            request.historical_data = _get_mock_stock_data(180)
        
        df = pd.DataFrame(request.historical_data)
        result = anomaly_service.train_detector(request.model, df)
        
        return {
            'status': 'success',
            'message': f"Détecteur {request.model} entraîné avec succès",
            'details': result,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """Liste les modèles de détection disponibles."""
    return {
        "models": [
            {
                "name": "isolation_forest",
                "description": "Isolation Forest - Détection par isolation",
                "best_for": "Détection rapide, données multi-dimensionnelles",
                "speed": "très rapide",
                "accuracy": "élevée",
                "requires_gpu": False,
                "status": "available",
            },
            {
                "name": "autoencoder",
                "description": "AutoEncoder - Réseau de neurones",
                "best_for": "Patterns complexes, relations non-linéaires",
                "speed": "moyen",
                "accuracy": "très élevée",
                "requires_gpu": True,
                "status": "available",
            },
            {
                "name": "one_class_svm",
                "description": "One-Class SVM - Classification mono-classe",
                "best_for": "Données avec peu d'anomalies connues",
                "speed": "lent",
                "accuracy": "bonne",
                "requires_gpu": False,
                "status": "available",
            },
        ],
        "anomaly_types": [
            {
                "type": "unusual_consumption",
                "description": "Consommation anormalement élevée",
                "severity": "high",
            },
            {
                "type": "potential_theft",
                "description": "Mouvement suspect pouvant indiquer un vol",
                "severity": "critical",
            },
            {
                "type": "stock_error",
                "description": "Erreur probable dans les données de stock",
                "severity": "medium",
            },
            {
                "type": "unusual_transfer",
                "description": "Transfert anormal entre entrepôts",
                "severity": "medium",
            },
            {
                "type": "expiry_risk",
                "description": "Risque de péremption détecté",
                "severity": "high",
            },
            {
                "type": "price_anomaly",
                "description": "Anomalie dans les prix unitaires",
                "severity": "low",
            },
        ],
    }


def _get_mock_stock_data(days: int = 90) -> List[Dict[str, Any]]:
    """Génère des données de stock simulées avec anomalies."""
    import numpy as np
    
    base_date = datetime.now() - timedelta(days=days)
    np.random.seed(42)
    
    data = []
    for i in range(days):
        quantity = np.random.normal(100, 15)
        
        # Injecter quelques anomalies
        if i in [20, 45, 72]:
            quantity = np.random.choice([0, 500, -10])
        
        data.append({
            'date': (base_date + timedelta(days=i)).strftime('%Y-%m-%d'),
            'quantity': max(0, round(quantity, 2)),
            'unit_price': round(np.random.normal(1500, 100), 2),
            'product_id': 'PROD-001',
            'warehouse_id': 'WH-001',
        })
    
    return data


def _get_anomaly_context(anomaly: Dict) -> str:
    """Fournit un contexte pour l'anomalie."""
    anomaly_type = anomaly.get('type', '')
    contexts = {
        'unusual_consumption': 'La consommation de ce produit dépasse largement la moyenne historique.',
        'potential_theft': 'Un mouvement suspect a été détecté en dehors des heures normales.',
        'stock_error': 'Les quantités enregistrées semblent incohérentes avec l\'historique.',
        'unusual_transfer': 'Ce transfert sort des patterns habituels.',
        'expiry_risk': 'Des produits approchent de leur date de péremption sans mouvement.',
        'price_anomaly': 'Le prix unitaire diffère significativement de la normale.',
    }
    return contexts.get(anomaly_type, 'Anomalie détectée par le système.')


def _get_recommended_action(anomaly: Dict) -> str:
    """Recommande une action pour l'anomalie."""
    severity = anomaly.get('severity', 'medium')
    anomaly_type = anomaly.get('type', '')
    
    actions = {
        ('critical', 'potential_theft'): '🚨 Vérifier immédiatement les caméras et les logs d\'accès. Contacter la sécurité.',
        ('high', 'unusual_consumption'): '📊 Analyser la cause de la surconsommation. Vérifier auprès du département concerné.',
        ('high', 'expiry_risk'): '⚠️ Planifier une utilisation prioritaire ou un retour fournisseur.',
        ('medium', 'stock_error'): '🔍 Effectuer un comptage physique pour vérifier le stock réel.',
        ('medium', 'unusual_transfer'): '📋 Vérifier le bon de transfert et contacter les deux entrepôts.',
        ('low', 'price_anomaly'): '💰 Vérifier le prix avec le fournisseur et mettre à jour si nécessaire.',
    }
    
    key = (severity, anomaly_type)
    if key in actions:
        return actions[key]
    
    if severity == 'critical':
        return '🚨 Action immédiate requise. Escalader au superviseur.'
    elif severity == 'high':
        return '⚠️ Investigation recommandée dans les 24h.'
    elif severity == 'medium':
        return '📋 Vérification à planifier cette semaine.'
    return '📝 Surveiller l\'évolution.'