# Script complet d'installation et seeding IUC
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IUC INVENTORY SYSTEM - SETUP COMPLET" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path $PSScriptRoot -Parent

# 1. Vérifier Docker
Write-Host "1. Vérification Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Docker n'est pas en cours d'exécution. Démarrage..." -ForegroundColor Red
    # Démarrer Docker Desktop si sur Windows
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "Veuillez attendre que Docker soit prêt, puis relancez ce script." -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Docker est prêt" -ForegroundColor Green

# 2. Démarrer les services
Write-Host ""
Write-Host "2. Démarrage des services..." -ForegroundColor Yellow
cd "$ProjectRoot\docker"

# Vérifier si .env existe
if (-not (Test-Path ".env")) {
    Write-Host "Création du fichier .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Fichier .env créé (vérifiez les paramètres si nécessaire)" -ForegroundColor Green
}

docker-compose up -d 2>&1
Write-Host "✓ Services démarrés" -ForegroundColor Green

# 3. Attendre que les services soient prêts
Write-Host ""
Write-Host "3. Attente des services..." -ForegroundColor Yellow
Write-Host "Attente de PostgreSQL..."
do {
    $pgReady = docker exec iuc_postgres pg_isready -U iuc_user 2>&1
    Start-Sleep -Seconds 2
} while ($pgReady -notmatch "accepting connections")
Write-Host "✓ PostgreSQL prêt" -ForegroundColor Green

Write-Host "Attente du backend..."
do {
    $backendReady = try {
        Invoke-WebRequest -Uri "http://localhost:8000/health/" -Method GET -TimeoutSec 2 | Select-Object -ExpandProperty StatusCode
    } catch { $null }
    Start-Sleep -Seconds 3
} while ($backendReady -ne 200)
Write-Host "✓ Backend prêt" -ForegroundColor Green

# 4. Exécuter les migrations
Write-Host ""
Write-Host "4. Exécution des migrations..." -ForegroundColor Yellow
docker exec iuc_backend python manage.py migrate --noinput
Write-Host "✓ Migrations exécutées" -ForegroundColor Green

# 5. Initialiser les rôles
Write-Host ""
Write-Host "5. Initialisation des rôles..." -ForegroundColor Yellow
docker exec iuc_backend python manage.py init_roles
Write-Host "✓ Rôles initialisés" -ForegroundColor Green

# 6. Seeding des données IUC
Write-Host ""
Write-Host "6. Seeding des données IUC..." -ForegroundColor Yellow
Write-Host "Ceci va créer toutes les données de test." -ForegroundColor Gray
docker exec iuc_backend python manage.py seed_iuc_data --force
Write-Host "✓ Données IUC créées" -ForegroundColor Green

# 7. Collecter les fichiers statiques
Write-Host ""
Write-Host "7. Collecte des fichiers statiques..." -ForegroundColor Yellow
docker exec iuc_backend python manage.py collectstatic --noinput
Write-Host "✓ Fichiers statiques collectés" -ForegroundColor Green

# 8. Résumé
Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "  ✅ INSTALLATION TERMINÉE !" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 URLs :" -ForegroundColor Yellow
Write-Host "  Frontend   : http://localhost:3000" -ForegroundColor White
Write-Host "  API Swagger: http://localhost:8000/swagger/" -ForegroundColor White
Write-Host "  Admin      : http://localhost:8000/admin/" -ForegroundColor White
Write-Host "  Grafana    : http://localhost:3001 (admin/admin)" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Comptes (mot de passe: IUC@2026!)" -ForegroundColor Yellow
Write-Host "  Admin      : admin@iuc.cm" -ForegroundColor White
Write-Host "  Manager    : directeur.logistique@iuc.cm" -ForegroundColor White
Write-Host "  Opérateur  : magasinier1@iuc.cm" -ForegroundColor White
Write-Host "  Superviseur: superviseur.stock@iuc.cm" -ForegroundColor White
Write-Host "  Viewer     : chef.info@iuc.cm" -ForegroundColor White
Write-Host "  Auditeur   : auditeur@iuc.cm" -ForegroundColor White
Write-Host ""
Write-Host "📊 Données créées :" -ForegroundColor Yellow
Write-Host "  • 4 Campus (Douala, Bonabéri, Yaoundé, Bafoussam)" -ForegroundColor White
Write-Host "  • 21 Départements" -ForegroundColor White
Write-Host "  • 18 Utilisateurs (tous les rôles)" -ForegroundColor White
Write-Host "  • 7 Entrepôts" -ForegroundColor White
Write-Host "  • 20+ Catégories" -ForegroundColor White
Write-Host "  • 10 Fournisseurs" -ForegroundColor White
Write-Host "  • 30+ Produits" -ForegroundColor White
Write-Host "  • ~100 Entrées de stock" -ForegroundColor White
Write-Host "  • ~200 Mouvements" -ForegroundColor White
Write-Host "  • 15 Commandes" -ForegroundColor White
Write-Host "  • 3 Inventaires" -ForegroundColor White
Write-Host ""