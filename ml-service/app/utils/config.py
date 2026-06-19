"""Configuration du microservice ML."""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Paramètres de l'application."""
    
    # Application
    APP_NAME: str = "IUC Inventory ML Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Serveur
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # Sécurité
    API_KEY: str = "ml-service-api-key-change-in-production"
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]
    
    # Base de données
    DATABASE_URL: str = "postgresql://iuc_user:iuc_password@localhost:5432/iuc_inventory"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "iuc-inventory"
    
    # Chemins des modèles
    MODELS_DIR: str = os.path.join(os.path.dirname(__file__), "../../data/models")
    
    # Modèles
    FORECASTING_MODEL: str = "prophet"  # prophet, xgboost, lstm
    ANOMALY_MODEL: str = "isolation_forest"  # isolation_forest, autoencoder
    OCR_ENGINE: str = "easyocr"  # easyocr, tesseract
    
    # LLM (Chatbot)
    LLM_MODEL: str = "google/flan-t5-base"  # Modèle par défaut
    LLM_API_KEY: str = ""
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Sentry
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()