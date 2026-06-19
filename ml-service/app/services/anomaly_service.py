"""
Service de détection d'anomalies dans les stocks.
Implémente Isolation Forest, AutoEncoder et One-Class SVM.
"""
import os
import pickle
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.metrics import classification_report
from app.utils.config import settings

logger = logging.getLogger(__name__)


class BaseAnomalyDetector:
    """Classe de base pour les détecteurs d'anomalies."""
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.threshold = None
        self.feature_names = []
    
    def fit(self, data: pd.DataFrame) -> None:
        """Entraîne le détecteur."""
        raise NotImplementedError
    
    def detect(self, data: pd.DataFrame) -> pd.DataFrame:
        """Détecte les anomalies."""
        raise NotImplementedError
    
    def save(self, path: str) -> None:
        """Sauvegarde le modèle."""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'threshold': self.threshold,
                'feature_names': self.feature_names,
            }, f)
    
    def load(self, path: str) -> None:
        """Charge un modèle sauvegardé."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.threshold = data['threshold']
            self.feature_names = data['feature_names']
            self.is_fitted = True
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prépare les features pour la détection."""
        df = data.copy()
        
        # Features de base
        features = []
        
        if 'quantity' in df.columns:
            features.append(df['quantity'].values)
        
        if 'unit_price' in df.columns:
            features.append(df['unit_price'].values)
        
        # Features temporelles
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            features.append(df['date'].dt.dayofweek.values)
            features.append(df['date'].dt.month.values)
            features.append(df['date'].dt.day.values)
        
        # Features calculées
        if 'quantity' in df.columns:
            # Variation jour par jour
            df['qty_change'] = df['quantity'].diff().fillna(0)
            features.append(df['qty_change'].values)
            
            # Z-score
            mean_qty = df['quantity'].mean()
            std_qty = df['quantity'].std()
            if std_qty > 0:
                df['zscore'] = (df['quantity'] - mean_qty) / std_qty
            else:
                df['zscore'] = 0
            features.append(df['zscore'].values)
            
            # Moyenne mobile
            df['rolling_mean_7'] = df['quantity'].rolling(7, min_periods=1).mean()
            df['deviation'] = df['quantity'] - df['rolling_mean_7']
            features.append(df['deviation'].values)
        
        if len(features) == 0:
            return np.zeros((len(data), 1))
        
        X = np.column_stack(features)
        X = np.nan_to_num(X, nan=0.0)
        
        return X


class IsolationForestDetector(BaseAnomalyDetector):
    """Détection d'anomalies par Isolation Forest."""
    
    def __init__(self, contamination: float = 0.1):
        super().__init__('isolation_forest')
        self.contamination = contamination
    
    def fit(self, data: pd.DataFrame) -> None:
        """Entraîne le modèle Isolation Forest."""
        try:
            # Préparer les features
            X = self._prepare_features(data)
            self.feature_names = [f'feature_{i}' for i in range(X.shape[1])]
            
            # Normaliser
            X_scaled = self.scaler.fit_transform(X)
            
            # Créer et entraîner
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100,
                max_samples='auto',
                bootstrap=False,
            )
            
            self.model.fit(X_scaled)
            
            # Calculer le seuil de décision
            scores = self.model.decision_function(X_scaled)
            self.threshold = np.percentile(scores, self.contamination * 100)
            
            self.is_fitted = True
            
            n_anomalies = (self.model.predict(X_scaled) == -1).sum()
            logger.info(
                f"Isolation Forest entraîné - {n_anomalies} anomalies détectées "
                f"({n_anomalies/len(data)*100:.1f}%)"
            )
            
        except Exception as e:
            logger.error(f"Erreur entraînement Isolation Forest: {e}")
            raise
    
    def detect(self, data: pd.DataFrame) -> pd.DataFrame:
        """Détecte les anomalies."""
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné")
        
        X = self._prepare_features(data)
        X_scaled = self.scaler.transform(X)
        
        # Prédictions (-1 = anomalie, 1 = normal)
        predictions = self.model.predict(X_scaled)
        
        # Scores d'anomalie (plus bas = plus anormal)
        scores = self.model.decision_function(X_scaled)
        
        # Normaliser les scores entre 0 et 1 (1 = très anormal)
        normalized_scores = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        
        result = data.copy()
        result['is_anomaly'] = predictions == -1
        result['anomaly_score'] = normalized_scores
        result['severity'] = result['anomaly_score'].apply(self._get_severity)
        
        return result
    
    def _get_severity(self, score: float) -> str:
        """Détermine la sévérité selon le score."""
        if score > 0.9:
            return 'critical'
        elif score > 0.7:
            return 'high'
        elif score > 0.5:
            return 'medium'
        return 'low'


class AutoEncoderDetector(BaseAnomalyDetector):
    """Détection d'anomalies par AutoEncoder."""
    
    def __init__(self, encoding_dim: int = 8, threshold_percentile: float = 95):
        super().__init__('autoencoder')
        self.encoding_dim = encoding_dim
        self.threshold_percentile = threshold_percentile
    
    def fit(self, data: pd.DataFrame) -> None:
        """Entraîne l'AutoEncoder."""
        try:
            import tensorflow as tf
            
            X = self._prepare_features(data)
            self.feature_names = [f'feature_{i}' for i in range(X.shape[1])]
            X_scaled = self.scaler.fit_transform(X)
            
            input_dim = X_scaled.shape[1]
            
            # Architecture de l'AutoEncoder
            input_layer = tf.keras.layers.Input(shape=(input_dim,))
            
            # Encodeur
            encoded = tf.keras.layers.Dense(32, activation='relu')(input_layer)
            encoded = tf.keras.layers.Dropout(0.2)(encoded)
            encoded = tf.keras.layers.Dense(16, activation='relu')(encoded)
            encoded = tf.keras.layers.Dense(self.encoding_dim, activation='relu')(encoded)
            
            # Décodeur
            decoded = tf.keras.layers.Dense(16, activation='relu')(encoded)
            decoded = tf.keras.layers.Dropout(0.2)(decoded)
            decoded = tf.keras.layers.Dense(32, activation='relu')(decoded)
            decoded = tf.keras.layers.Dense(input_dim, activation='linear')(decoded)
            
            self.model = tf.keras.Model(input_layer, decoded)
            self.model.compile(optimizer='adam', loss='mse')
            
            # Early stopping
            early_stop = tf.keras.callbacks.EarlyStopping(
                monitor='loss',
                patience=10,
                restore_best_weights=True,
            )
            
            # Entraîner
            self.model.fit(
                X_scaled, X_scaled,
                epochs=50,
                batch_size=32,
                shuffle=True,
                validation_split=0.1,
                callbacks=[early_stop],
                verbose=0,
            )
            
            # Calculer le seuil basé sur l'erreur de reconstruction
            reconstructions = self.model.predict(X_scaled, verbose=0)
            mse = np.mean(np.square(X_scaled - reconstructions), axis=1)
            self.threshold = np.percentile(mse, self.threshold_percentile)
            
            self.is_fitted = True
            
            n_anomalies = (mse > self.threshold).sum()
            logger.info(
                f"AutoEncoder entraîné - {n_anomalies} anomalies détectées "
                f"({n_anomalies/len(data)*100:.1f}%)"
            )
            
        except ImportError:
            logger.warning("TensorFlow non installé")
            raise
        except Exception as e:
            logger.error(f"Erreur entraînement AutoEncoder: {e}")
            raise
    
    def detect(self, data: pd.DataFrame) -> pd.DataFrame:
        """Détecte les anomalies."""
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné")
        
        X = self._prepare_features(data)
        X_scaled = self.scaler.transform(X)
        
        # Erreur de reconstruction
        reconstructions = self.model.predict(X_scaled, verbose=0)
        mse = np.mean(np.square(X_scaled - reconstructions), axis=1)
        
        # Normaliser les scores
        normalized_scores = np.clip(mse / self.threshold, 0, 1)
        
        result = data.copy()
        result['is_anomaly'] = mse > self.threshold
        result['anomaly_score'] = normalized_scores
        result['reconstruction_error'] = mse
        result['severity'] = result['anomaly_score'].apply(self._get_severity)
        
        return result
    
    def _get_severity(self, score: float) -> str:
        if score > 0.9:
            return 'critical'
        elif score > 0.7:
            return 'high'
        elif score > 0.5:
            return 'medium'
        return 'low'


class OneClassSVMDetector(BaseAnomalyDetector):
    """Détection d'anomalies par One-Class SVM."""
    
    def __init__(self, nu: float = 0.1, kernel: str = 'rbf'):
        super().__init__('one_class_svm')
        self.nu = nu
        self.kernel = kernel
    
    def fit(self, data: pd.DataFrame) -> None:
        """Entraîne le One-Class SVM."""
        try:
            X = self._prepare_features(data)
            self.feature_names = [f'feature_{i}' for i in range(X.shape[1])]
            X_scaled = self.scaler.fit_transform(X)
            
            self.model = OneClassSVM(
                nu=self.nu,
                kernel=self.kernel,
                gamma='scale',
            )
            
            self.model.fit(X_scaled)
            
            scores = self.model.decision_function(X_scaled)
            self.threshold = np.percentile(scores, self.nu * 100)
            
            self.is_fitted = True
            
            n_anomalies = (self.model.predict(X_scaled) == -1).sum()
            logger.info(
                f"One-Class SVM entraîné - {n_anomalies} anomalies détectées "
                f"({n_anomalies/len(data)*100:.1f}%)"
            )
            
        except Exception as e:
            logger.error(f"Erreur entraînement One-Class SVM: {e}")
            raise
    
    def detect(self, data: pd.DataFrame) -> pd.DataFrame:
        """Détecte les anomalies."""
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné")
        
        X = self._prepare_features(data)
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        normalized_scores = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        
        result = data.copy()
        result['is_anomaly'] = predictions == -1
        result['anomaly_score'] = normalized_scores
        result['severity'] = result['anomaly_score'].apply(
            lambda s: 'critical' if s > 0.9 else 'high' if s > 0.7 else 'medium' if s > 0.5 else 'low'
        )
        
        return result


class AnomalyDetectionService:
    """Service unifié de détection d'anomalies."""
    
    def __init__(self):
        self.detectors = {
            'isolation_forest': IsolationForestDetector,
            'autoencoder': AutoEncoderDetector,
            'one_class_svm': OneClassSVMDetector,
        }
        self.active_detectors: Dict[str, BaseAnomalyDetector] = {}
    
    def get_or_create_detector(self, model_name: str) -> BaseAnomalyDetector:
        """Récupère ou crée un détecteur."""
        if model_name in self.active_detectors:
            return self.active_detectors[model_name]
        
        model_path = os.path.join(settings.MODELS_DIR, f'anomaly_{model_name}.pkl')
        
        if model_name not in self.detectors:
            raise ValueError(f"Détecteur inconnu: {model_name}")
        
        detector = self.detectors[model_name]()
        
        if os.path.exists(model_path):
            detector.load(model_path)
            self.active_detectors[model_name] = detector
        
        return detector
    
    def train_detector(self, model_name: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Entraîne un détecteur."""
        detector = self.detectors[model_name]()
        detector.fit(data)
        
        model_path = os.path.join(settings.MODELS_DIR, f'anomaly_{model_name}.pkl')
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        detector.save(model_path)
        
        self.active_detectors[model_name] = detector
        
        return {
            'model': model_name,
            'is_fitted': True,
            'saved_to': model_path,
        }
    
    def detect_anomalies(
        self, model_name: str, data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Détecte les anomalies dans les données."""
        detector = self.get_or_create_detector(model_name)
        
        if not detector.is_fitted:
            detector.fit(data)
        
        results = detector.detect(data)
        
        anomalies = results[results['is_anomaly']].copy()
        
        # Formater les résultats
        anomaly_list = []
        for idx, row in anomalies.iterrows():
            anomaly_list.append({
                'id': f"anomaly_{idx}_{datetime.now().timestamp()}",
                'type': self._classify_anomaly(row),
                'severity': row.get('severity', 'medium'),
                'score': float(row.get('anomaly_score', 0)),
                'details': {
                    'date': str(row.get('date', '')),
                    'quantity': float(row.get('quantity', 0)),
                    'expected_range': self._get_expected_range(data, row),
                    'deviation': self._calculate_deviation(data, row),
                },
                'detected_at': datetime.now().isoformat(),
            })
        
        return {
            'model': model_name,
            'total_records': len(data),
            'anomalies_found': len(anomaly_list),
            'anomaly_rate': round(len(anomaly_list) / max(len(data), 1) * 100, 2),
            'anomalies': anomaly_list,
            'threshold': float(detector.threshold) if detector.threshold else None,
            'detection_date': datetime.now().isoformat(),
        }
    
    def _classify_anomaly(self, row: pd.Series) -> str:
        """Classifie le type d'anomalie."""
        quantity = row.get('quantity', 0)
        deviation = row.get('deviation', 0)
        
        if quantity == 0:
            return 'stock_error'
        elif deviation and abs(deviation) > 100:
            return 'unusual_consumption' if deviation < 0 else 'unusual_entry'
        elif row.get('anomaly_score', 0) > 0.8:
            return 'potential_theft'
        return 'unknown_anomaly'
    
    def _get_expected_range(self, data: pd.DataFrame, row: pd.Series) -> Dict:
        """Calcule la plage attendue."""
        qty_col = 'quantity' if 'quantity' in data.columns else None
        if qty_col:
            mean = data[qty_col].mean()
            std = data[qty_col].std()
            return {
                'mean': float(mean),
                'lower': float(mean - 2 * std),
                'upper': float(mean + 2 * std),
            }
        return {'mean': 0, 'lower': 0, 'upper': 0}
    
    def _calculate_deviation(self, data: pd.DataFrame, row: pd.Series) -> float:
        """Calcule la déviation."""
        qty_col = 'quantity' if 'quantity' in data.columns else None
        if qty_col:
            mean = data[qty_col].mean()
            return float(row.get('quantity', 0) - mean)
        return 0.0


# Instance globale
anomaly_service = AnomalyDetectionService()