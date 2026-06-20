from django.http import JsonResponse
from django.db import connections

def health_check(request):
    status = {
        "status": "healthy",
        "application": "IUC Inventory System",
        "version": "1.0.0",
        "checks": {},
    }
    try:
        db_conn = connections["default"]
        db_conn.cursor()
        status["checks"]["database"] = "connected"
    except Exception as e:
        status["checks"]["database"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
    return JsonResponse(status)