"""
Service de prévision de consommation.
Implémente Prophet, XGBoost et LSTM.
"""
import os
import pickle
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from app.utils.config import settings

logger = logging.getLogger(__name__)


class BaseForecaster:
    """Classe de base pour les modèles de prévision."""
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.is_fitted = False
        self.metrics = {}
    
    def fit(self, data: pd.DataFrame) -> None:
        """Entraîne le modèle."""
        raise NotImplementedError
    
    def predict(self, horizon: int) -> np.ndarray:
        """Prédit sur l'horizon donné."""
        raise NotImplementedError
    
    def save(self, path: str) -> None:
        """Sauvegarde le modèle."""
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path: str) -> 'BaseForecaster':
        """Charge un modèle sauvegardé."""
        with open(path, 'rb') as f:
            return pickle.load(f)
    
    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Évalue les performances du modèle."""
        return {
            'mae': mean_absolute_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mape': np.mean(np.abs((y_true - y_pred) / np.where(y_true != 0, y_true, 1))) * 100,
        }


class ProphetForecaster(BaseForecaster):
    """Prévision avec Facebook Prophet."""
    
    def __init__(self):
        super().__init__('prophet')
        self.model = None
    
    def fit(self, data: pd.DataFrame) -> None:
        """Entraîne le modèle Prophet."""
        try:
            from prophet import Prophet
            
            # Préparer les données pour Prophet
            df = data.rename(columns={'date': 'ds', 'quantity': 'y'})
            
            # Créer et entraîner le modèle
            self.model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0,
            )
            
            # Ajouter des saisonnalités personnalisées si nécessaire
            if len(df) >= 60:
                self.model.add_seasonality(
                    name='monthly',
                    period=30.5,
                    fourier_order=5
                )
            
            self.model.fit(df)
            self.is_fitted = True
            
            # Calculer les métriques sur l'ensemble d'entraînement
            forecast = self.model.predict(df[['ds']])
            self.metrics = self.evaluate(df['y'].values, forecast['yhat'].values)
            
            logger.info(f"Prophet entraîné - MAE: {self.metrics['mae']:.2f}")
            
        except ImportError:
            logger.warning("Prophet non installé. Installation: pip install prophet")
            raise
        except Exception as e:
            logger.error(f"Erreur entraînement Prophet: {e}")
            raise
    
    def predict(self, horizon: int) -> np.ndarray:
        """Prédit les valeurs futures."""
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné")
        
        # Créer le dataframe futur
        future = self.model.make_future_dataframe(periods=horizon)
        forecast = self.model.predict(future)
        
        # Retourner les prédictions
        predictions = forecast.tail(horizon)['yhat'].values
        lower = forecast.tail(horizon)['yhat_lower'].values
        upper = forecast.tail(horizon)['yhat_upper'].values
        
        return predictions, lower, upper


class XGBoostForecaster(BaseForecaster):
    """Prévision avec XGBoost."""
    
    def __init__(self):
        super().__init__('xgboost')
        self.model = None
        self.feature_columns = []
    
    def fit(self, data: pd.DataFrame) -> None:
        """Entraîne le modèle XGBoost."""
        try:
            import xgboost as xgb
            
            # Créer les features
            df = self._create_features(data)
            
            # Définir features et target
            feature_cols = [c for c in df.columns if c not in ['date', 'quantity', 'target']]
            self.feature_columns = feature_cols
            
            X = df[feature_cols].values
            y = df['target'].values
            
            # Split train/test
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Créer et entraîner le modèle
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                objective='reg:squarederror',
            )
            
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                verbose=False,
            )
            
            self.is_fitted = True
            
            # Évaluer
            y_pred = self.model.predict(X_test)
            self.metrics = self.evaluate(y_test, y_pred)
            
            logger.info(f"XGBoost entraîné - MAE: {self.metrics['mae']:.2f}")
            
        except ImportError:
            logger.warning("XGBoost non installé. Installation: pip install xgboost")
            raise
    
    def predict(self, horizon: int) -> np.ndarray:
        """Prédit les valeurs futures."""
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné")
        
        # Pour XGBoost, on prédit pas à pas
        # Cette implémentation simplifiée retourne la moyenne mobile
        predictions = []
        last_value = 0  # À remplacer par la dernière valeur connue
        
        for i in range(horizon):
            # Créer les features pour ce point
            features = self._create_prediction_features(i, last_value)
            pred = self.model.predict([features])[0]
            predictions.append(max(0, pred))
            last_value = pred
        
        predictions = np.array(predictions)
        lower = predictions * 0.8
        upper = predictions * 1.2
        
        return predictions, lower, upper
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crée des features pour l'entraînement."""
        df = df.copy()
        
        # Features temporelles
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['dayofweek'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            df['quarter'] = df['date'].dt.quarter
            df['dayofyear'] = df['date'].dt.dayofyear
            df['weekofyear'] = df['date'].dt.isocalendar().week.astype(int)
        
        # Lags
        if 'quantity' in df.columns:
            for lag in [1, 2, 3, 7, 14, 30]:
                df[f'lag_{lag}'] = df['quantity'].shift(lag)
            
            # Moyennes mobiles
            for window in [3, 7, 14]:
                df[f'rolling_mean_{window}'] = df['quantity'].rolling(window).mean()
                df[f'rolling_std_{window}'] = df['quantity'].rolling(window).std()
        
        # Target (valeur à prédire = prochaine valeur)
        if 'quantity' in df.columns:
            df['target'] = df['quantity'].shift(-1)
        
        # Supprimer les NaN
        df = df.dropna()
        
        return df
    
    def _create_prediction_features(self, step: int, last_value: float) -> List[float]:
        """Crée les features pour une prédiction."""
        features = [0] * len(self.feature_columns)
        # Simplifié - à améliorer avec les vraies features
        return features


class LSTMForecaster(BaseForecaster):
    """Prévision avec LSTM (Deep Learning)."""
    
    def __init__(self, sequence_length: int = 30):
        super().__init__('lstm')
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = None
    
    def fit(self, data: pd.DataFrame) -> None:
        """Entraîne le modèle LSTM."""
        try:
            import tensorflow as tf
            from sklearn.preprocessing import MinMaxScaler
            
            # Préparer les données
            values = data['quantity'].values.reshape(-1, 1)
            
            # Normaliser
            self.scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_values = self.scaler.fit_transform(values)
            
            # Créer les séquences
            X, y = self._create_sequences(scaled_values)
            
            # Split
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Reshape pour LSTM [samples, timesteps, features]
            X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
            X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
            
            # Créer le modèle
            self.model = tf.keras.Sequential([
                tf.keras.layers.LSTM(50, activation='relu', return_sequences=True,
                                     input_shape=(self.sequence_length, 1)),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.LSTM(50, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(25, activation='relu'),
                tf.keras.layers.Dense(1),
            ])
            
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae'],
            )
            
            # Early stopping
            early_stop = tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
            )
            
            # Entraîner
            history = self.model.fit(
                X_train, y_train,
                epochs=100,
                batch_size=32,
                validation_data=(X_test, y_test),
                callbacks=[early_stop],
                verbose=0,
            )
            
            self.is_fitted = True
            
            # Évaluer
            y_pred = self.model.predict(X_test, verbose=0)
            y_test_inv = self.scaler.inverse_transform(y_test.reshape(-1, 1))
            y_pred_inv = self.scaler.inverse_transform(y_pred)
            
            self.metrics = self.evaluate(y_test_inv.flatten(), y_pred_inv.flatten())
            
            logger.info(f"LSTM entraîné - MAE: {self.metrics['mae']:.2f}")
            
        except ImportError as e:
            logger.warning(f"TensorFlow non installé: {e}")
            raise
    
    def predict(self, horizon: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prédit les valeurs futures."""
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné")
        
        # Prédiction itérative
        predictions = []
        last_sequence = self._get_last_sequence()
        
        for _ in range(horizon):
            seq = last_sequence.reshape((1, self.sequence_length, 1))
            pred = self.model.predict(seq, verbose=0)[0, 0]
            predictions.append(pred)
            
            # Mettre à jour la séquence
            last_sequence = np.roll(last_sequence, -1)
            last_sequence[-1] = pred
        
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions).flatten()
        
        lower = predictions * 0.85
        upper = predictions * 1.15
        
        return predictions, lower, upper
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Crée des séquences pour LSTM."""
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i + self.sequence_length])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def _get_last_sequence(self) -> np.ndarray:
        """Récupère la dernière séquence pour la prédiction."""
        # À implémenter avec les vraies données
        return np.zeros(self.sequence_length)


class ForecastingService:
    """Service de prévision unifié."""
    
    def __init__(self):
        self.forecasters = {
            'prophet': ProphetForecaster,
            'xgboost': XGBoostForecaster,
            'lstm': LSTMForecaster,
        }
        self.active_models: Dict[str, BaseForecaster] = {}
    
    def get_or_create_model(self, model_name: str) -> BaseForecaster:
        """Récupère ou crée un modèle."""
        if model_name in self.active_models:
            return self.active_models[model_name]
        
        # Essayer de charger depuis le disque
        model_path = os.path.join(settings.MODELS_DIR, f'forecaster_{model_name}.pkl')
        if os.path.exists(model_path):
            model = BaseForecaster.load(model_path)
            self.active_models[model_name] = model
            return model
        
        # Créer un nouveau modèle
        if model_name not in self.forecasters:
            raise ValueError(f"Modèle inconnu: {model_name}. Options: {list(self.forecasters.keys())}")
        
        model = self.forecasters[model_name]()
        return model
    
    def train_model(self, model_name: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Entraîne un modèle."""
        model = self.get_or_create_model(model_name)
        model.fit(data)
        
        # Sauvegarder
        model_path = os.path.join(settings.MODELS_DIR, f'forecaster_{model_name}.pkl')
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        model.save(model_path)
        
        self.active_models[model_name] = model
        
        return {
            'model': model_name,
            'metrics': model.metrics,
            'is_fitted': model.is_fitted,
            'saved_to': model_path,
        }
    
    def predict(self, model_name: str, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """Effectue une prévision."""
        model = self.get_or_create_model(model_name)
        
        if not model.is_fitted:
            # Entraîner rapidement si pas encore fait
            model.fit(data)
        
        predictions, lower, upper = model.predict(horizon)
        
        # Créer les dates futures
        last_date = data['date'].max() if 'date' in data.columns else datetime.now()
        future_dates = [
            (last_date + timedelta(days=i + 1)).strftime('%Y-%m-%d')
            for i in range(horizon)
        ]
        
        return {
            'model': model_name,
            'horizon': horizon,
            'forecasts': [
                {
                    'date': future_dates[i],
                    'predicted': round(float(predictions[i]), 2),
                    'lower_bound': round(float(lower[i]), 2),
                    'upper_bound': round(float(upper[i]), 2),
                }
                for i in range(horizon)
            ],
            'confidence_interval': {
                'lower': [round(float(l), 2) for l in lower],
                'upper': [round(float(u), 2) for u in upper],
            },
            'metrics': model.metrics,
            'generated_at': datetime.now().isoformat(),
        }
    
    def compare_models(self, data: pd.DataFrame, horizon: int = 30) -> Dict[str, Any]:
        """Compare les performances de tous les modèles."""
        results = {}
        
        for model_name in self.forecasters.keys():
            try:
                model = self.get_or_create_model(model_name)
                model.fit(data)
                results[model_name] = {
                    'metrics': model.metrics,
                    'status': 'success',
                }
            except Exception as e:
                results[model_name] = {
                    'status': 'failed',
                    'error': str(e),
                }
        
        # Déterminer le meilleur modèle
        best_model = None
        best_mae = float('inf')
        for name, result in results.items():
            if result['status'] == 'success':
                mae = result['metrics'].get('mae', float('inf'))
                if mae < best_mae:
                    best_mae = mae
                    best_model = name
        
        return {
            'results': results,
            'best_model': best_model,
            'best_mae': best_mae if best_model else None,
            'comparison_date': datetime.now().isoformat(),
        }


# Instance globale du service
forecasting_service = ForecastingService()