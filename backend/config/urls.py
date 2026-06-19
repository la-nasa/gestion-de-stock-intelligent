\"\"\"
URL Configuration for IUC Inventory System
\"\"\"
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title='IUC Inventory System API',
        default_version='v1',
        description='API de gestion de stock intelligente pour l\'Institut Universitaire de la Côte',
        terms_of_service='https://www.iuc.cm/terms/',
        contact=openapi.Contact(email='support@iuc.cm'),
        license=openapi.License(name='Proprietary'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API v1
    path('api/v1/', include('api.v1.urls')),
    
    # Health Check
    path('health/', include('core.urls')),
    
    # Root redirect
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
