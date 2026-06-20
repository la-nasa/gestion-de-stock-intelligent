from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>IUC Inventory API</h1><p><a href='/admin/'>Admin</a> | <a href='/api/v1/'>API</a></p>")

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.v1.urls")),
    path("health/", include("core.urls")),
]
