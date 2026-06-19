"""Configuration du microservice ML."""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Paramètres de l'application."""

    # Application
    APP_NAME: str = "IUC Inventory ML Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Serveur
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Sécurité - accepter une chaîne simple ou une liste JSON
    API_KEY: str = "ml-service-api-key-change-in-production"
    ALLOWED_HOSTS: str = "*"
    CORS_ORIGINS: str = "*"

    # Base de données (optionnelle)
    DATABASE_URL: str = ""

    # Redis (optionnel)
    REDIS_URL: str = ""

    # MLflow (optionnel)
    MLFLOW_TRACKING_URI: str = ""
    MLFLOW_EXPERIMENT_NAME: str = "iuc-inventory"

    # Chemins des modèles
    MODELS_DIR: str = os.path.join(os.path.dirname(__file__), "../../data/models")

    # LLM (Chatbot)
    LLM_MODEL: str = "google/flan-t5-base"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()