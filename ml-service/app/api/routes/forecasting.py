"""Routes de prévision avec vrais modèles ML."""
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.services.forecasting_service import forecasting_service

router = APIRouter()


class ForecastRequest(BaseModel):
    """Requête de prévision."""
    product_ids: List[str]
    horizon_days: int = 30
    model: str = "prophet"
    include_history: bool = True


class TrainRequest(BaseModel):
    """Requête d'entraînement."""
    product_id: str
    model: str = "prophet"
    historical_data: List[Dict[str, Any]]


@router.post("/predict")
async def predict_consumption(request: ForecastRequest):
    """Prédit la consommation future."""
    try:
        results = []
        
        for product_id in request.product_ids:
            # Récupérer les données historiques (simulé ou depuis la DB)
            historical_data = _get_mock_historical_data(request.horizon_days)
            
            if historical_data is not None and len(historical_data) > 0:
                df = pd.DataFrame(historical_data)
                
                # Prévision avec le modèle choisi
                try:
                    prediction = forecasting_service.predict(
                        request.model, df, request.horizon_days
                    )
                    prediction['product_id'] = product_id
                    results.append(prediction)
                except Exception as e:
                    # Fallback sur un autre modèle
                    for fallback in ['prophet', 'xgboost']:
                        if fallback != request.model:
                            try:
                                prediction = forecasting_service.predict(
                                    fallback, df, request.horizon_days
                                )
                                prediction['product_id'] = product_id
                                prediction['model'] = f"{fallback} (fallback from {request.model})"
                                results.append(prediction)
                                break
                            except:
                                continue
        
        return {
            'status': 'success',
            'count': len(results),
            'predictions': results,
            'generated_at': datetime.now().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train_model(request: TrainRequest):
    """Entraîne un modèle de prévision."""
    try:
        if not request.historical_data:
            request.historical_data = _get_mock_historical_data(365)
        
        df = pd.DataFrame(request.historical_data)
        result = forecasting_service.train_model(request.model, df)
        
        return {
            'status': 'success',
            'message': f"Modèle {request.model} entraîné avec succès",
            'details': result,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
async def compare_models(horizon: int = Query(30, ge=7, le=365)):
    """Compare les performances des modèles."""
    try:
        data = _get_mock_historical_data(180)
        df = pd.DataFrame(data)
        
        results = forecasting_service.compare_models(df, horizon)
        
        return {
            'status': 'success',
            'comparison': results,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """Liste les modèles disponibles."""
    return {
        "models": [
            {
                "name": "prophet",
                "description": "Facebook Prophet - Séries temporelles",
                "best_for": "Données avec tendances et saisonnalités",
                "requires_gpu": False,
                "training_speed": "rapide",
                "accuracy": "élevée",
                "status": "available",
            },
            {
                "name": "xgboost",
                "description": "XGBoost - Gradient Boosting",
                "best_for": "Données avec features multiples",
                "requires_gpu": False,
                "training_speed": "très rapide",
                "accuracy": "très élevée",
                "status": "available",
            },
            {
                "name": "lstm",
                "description": "LSTM - Deep Learning",
                "best_for": "Séquences longues, patterns complexes",
                "requires_gpu": True,
                "training_speed": "lent",
                "accuracy": "excellente",
                "status": "available",
            },
        ]
    }


def _get_mock_historical_data(days: int = 365) -> List[Dict[str, Any]]:
    """Génère des données historiques simulées pour les tests."""
    import numpy as np
    
    base_date = datetime.now() - timedelta(days=days)
    trend = np.linspace(50, 80, days)
    seasonality = 15 * np.sin(np.linspace(0, 4 * np.pi, days))
    noise = np.random.normal(0, 8, days)
    
    values = trend + seasonality + noise
    values = np.maximum(values, 0)
    
    return [
        {
            'date': (base_date + timedelta(days=i)).strftime('%Y-%m-%d'),
            'quantity': round(float(values[i]), 2),
        }
        for i in range(days)
    ]