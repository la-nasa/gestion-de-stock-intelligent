"""
URL Configuration for IUC Inventory System.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="fr">
    <head><meta charset="UTF-8"><title>IUC Inventory API</title>
    <style>body{font-family:Arial;max-width:800px;margin:50px auto;padding:20px;background:#f8fafc}
    h1{color:#1e40af}.card{background:white;padding:20px;border-radius:12px;margin:20px 0;box-shadow:0 2px 8px rgba(0,0,0,.05)}
    a{color:#0d9488;text-decoration:none}code{background:#e2e8f0;padding:2px 6px;border-radius:4px}</style></head>
    <body>
    <h1>🏛️ IUC Inventory System API</h1>
    <div class="card"><h2>✅ API en ligne</h2><p>L'API est opérationnelle.</p></div>
    <div class="card"><h2>📚 Documentation</h2><p>👉 <a href="/swagger/">Swagger UI</a></p><p>👉 <a href="/redoc/">ReDoc</a></p><p>👉 <a href="/admin/">Administration Django</a></p></div>
    <div class="card"><h2>🔑 Connexion</h2><p>Endpoint: <code>POST /api/v1/auth/login/</code></p><p>Compte admin: <code>admin@iuc.cm</code></p></div>
    <div class="card"><h2>🏥 Health Check</h2><p>👉 <a href="/health/">/health/</a></p></div>
    </body></html>""")

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('swagger/', include('drf_yasg.urls_custom')),
    path('api/v1/', include('api.v1.urls')),
    path('health/', include('core.urls')),
]