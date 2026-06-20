from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(title="IUC API", default_version="v1"),
    public=True,
    permission_classes=[AllowAny],
)

def home(request):
    return HttpResponse("<h1>IUC Inventory API</h1><p><a href='/swagger/'>Swagger</a> | <a href='/admin/'>Admin</a></p>")

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("swagger/", schema_view.with_ui("swagger"), name="swagger"),
    path("api/v1/", include("api.v1.urls")),
    path("health/", include("core.urls")),
]