# Script de déploiement complet sur hébergeurs gratuits
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DÉPLOIEMENT IUC INVENTORY SYSTEM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Que voulez-vous déployer ?`n1. Frontend (Vercel)`n2. Backend (Render)`n3. ML Service (Railway)`n4. Tout (recommandé)`nChoix"

# 1. FRONTEND → VERCEL
if ($choice -in @("1","4")) {
    Write-Host "`n📦 Déploiement Frontend sur Vercel..." -ForegroundColor Yellow
    Write-Host "  1. Allez sur https://vercel.com" -ForegroundColor White
    Write-Host "  2. Cliquez 'New Project'" -ForegroundColor White
    Write-Host "  3. Importez le dossier 'frontend/'" -ForegroundColor White
    Write-Host "  4. Variables d'environnement automatiques depuis .env.production" -ForegroundColor White
    Write-Host "  5. Cliquez 'Deploy'" -ForegroundColor White
    Write-Host ""
    Write-Host "  OU via CLI :" -ForegroundColor Gray
    Write-Host "  cd frontend" -ForegroundColor White
    Write-Host "  npm i -g vercel" -ForegroundColor White
    Write-Host "  vercel --prod" -ForegroundColor White
}

# 2. BACKEND → RENDER
if ($choice -in @("2","4")) {
    Write-Host "`n📦 Déploiement Backend sur Render..." -ForegroundColor Yellow
    Write-Host "  1. Allez sur https://render.com" -ForegroundColor White
    Write-Host "  2. Créez un compte gratuit" -ForegroundColor White
    Write-Host "  3. Cliquez 'New +' → 'Web Service'" -ForegroundColor White
    Write-Host "  4. Connectez votre repo GitHub" -ForegroundColor White
    Write-Host "  5. Root Directory: backend/" -ForegroundColor White
    Write-Host "  6. Build Command: pip install -r requirements.txt && python manage.py migrate" -ForegroundColor White
    Write-Host "  7. Start Command: gunicorn config.wsgi:application" -ForegroundColor White
    Write-Host "  8. Ajoutez les variables d'environnement" -ForegroundColor White
    Write-Host ""
    Write-Host "  URL: https://iuc-api.onrender.com" -ForegroundColor Green
}

# 3. ML SERVICE → RAILWAY
if ($choice -in @("3","4")) {
    Write-Host "`n📦 Déploiement ML Service sur Railway..." -ForegroundColor Yellow
    Write-Host "  1. Allez sur https://railway.app" -ForegroundColor White
    Write-Host "  2. Créez un compte gratuit" -ForegroundColor White
    Write-Host "  3. 'New Project' → 'Deploy from GitHub'" -ForegroundColor White
    Write-Host "  4. Sélectionnez le dossier ml-service/" -ForegroundColor White
    Write-Host "  5. Railway détecte automatiquement Python/FastAPI" -ForegroundColor White
    Write-Host ""
    Write-Host "  URL: https://iuc-ml.up.railway.app" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "  ✅ Instructions prêtes !" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 URLs après déploiement :" -ForegroundColor Yellow
Write-Host "  Frontend  : https://iuc-inventory.vercel.app" -ForegroundColor White
Write-Host "  API       : https://iuc-api.onrender.com" -ForegroundColor White
Write-Host "  ML Service: https://iuc-ml.up.railway.app" -ForegroundColor White
Write-Host "  API Docs  : https://iuc-api.onrender.com/swagger/" -ForegroundColor White