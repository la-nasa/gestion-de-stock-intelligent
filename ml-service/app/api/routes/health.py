"""Routes de health check."""
from fastapi import APIRouter
from datetime import datetime
import psutil

router = APIRouter()


@router.get("/health")
async def health_check():
    """Vérification de l'état du service."""
    return {
        "status": "healthy",
        "service": "IUC ML Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
    }


@router.get("/health/detailed")
async def detailed_health():
    """Vérification détaillée avec métriques système."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_used_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_used_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
        },
        "models": {
            "forecasting": "loaded",
            "anomaly_detection": "loaded",
            "ocr": "loaded",
        }
    }


@router.get("/metrics")
async def metrics():
    """Métriques Prometheus."""
    return {
        "requests_total": 0,
        "predictions_total": 0,
        "model_load_time_ms": 0,
    }