"""
Microservice IA/ML - IUC Inventory System
FastAPI application principale.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api.routes import forecasting, anomaly, ocr, chatbot, health
from app.utils.config import settings

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cycle de vie de l'application."""
    logger.info("=" * 50)
    logger.info("🚀 Démarrage du Microservice IA IUC...")
    logger.info(f"   Environnement: {settings.ENVIRONMENT}")
    logger.info(f"   Version: {settings.APP_VERSION}")
    logger.info("=" * 50)
    
    # Chargement des modèles au démarrage
    await load_models()
    
    yield
    
    # Nettoyage à l'arrêt
    logger.info("Arrêt du microservice IA...")
    await cleanup_models()


async def load_models():
    """Charge les modèles ML au démarrage."""
    try:
        logger.info("📦 Chargement des modèles ML...")
        # Les modèles seront chargés à la demande (lazy loading)
        logger.info("✓ Modèles prêts (chargement différé)")
    except Exception as e:
        logger.error(f"Erreur chargement modèles: {e}")


async def cleanup_models():
    """Nettoie les ressources."""
    logger.info("✓ Nettoyage terminé")


# Création de l'application
app = FastAPI(
    title="IUC Inventory - ML Service",
    description="""
    Microservice d'Intelligence Artificielle pour la gestion de stock.
    
    ## Fonctionnalités :
    * **Prévisions** : Prédiction de la consommation future
    * **Détection d'anomalies** : Identification de comportements suspects
    * **OCR** : Extraction de données de factures
    * **Chatbot** : Assistant IA conversationnel
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "IUC DSI",
        "email": "support@iuc.cm",
    },
    license_info={
        "name": "Propriétaire - IUC",
    },
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware Trusted Hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)


# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log les requêtes entrantes."""
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"← {response.status_code}")
    return response


# Middleware de vérification API Key
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """Vérifie la clé API pour les routes protégées."""
    if request.url.path.startswith("/api/v1/"):
        api_key = request.headers.get("X-API-Key")
        if api_key != settings.API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Clé API invalide"}
            )
    return await call_next(request)


# Inclusion des routeurs
app.include_router(health.router, tags=["Health"])
app.include_router(forecasting.router, prefix="/api/v1/forecasting", tags=["Forecasting"])
app.include_router(anomaly.router, prefix="/api/v1/anomaly", tags=["Anomaly Detection"])
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["Chatbot"])


@app.get("/")
async def root():
    """Racine du service."""
    return {
        "service": "IUC Inventory - ML Service",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "forecasting": "/api/v1/forecasting/",
            "anomaly": "/api/v1/anomaly/",
            "ocr": "/api/v1/ocr/",
            "chatbot": "/api/v1/chatbot/",
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )