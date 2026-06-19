"""URLs de l'API v1."""
from django.urls import path, include

app_name = 'api-v1'

urlpatterns = [
    path('', include('api.v1.auth_urls')),
    path('', include('api.v1.rbac_urls')),
    path('', include('api.v1.product_urls')),
    path('', include('api.v1.stock_urls')),
    path('', include('api.v1.dashboard_urls')),
    path('', include('api.v1.inventory_urls')),
    path('', include('api.v1.report_urls')),
    path('', include('api.v1.qr_urls')),
    path('', include('api.v1.notification_urls')),
    path('', include('api.v1.ocr_urls')),
    path('health/', include('core.urls')),
]