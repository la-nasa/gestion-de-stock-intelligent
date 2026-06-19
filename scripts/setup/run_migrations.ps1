# Script PowerShell pour exécuter les migrations Django
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IUC Inventory - Migrations" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

cd $PSScriptRoot\..\..\backend

# Activer l'environnement virtuel si présent
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
    . .\venv\Scripts\Activate.ps1
}

Write-Host "1. Création des migrations..." -ForegroundColor Yellow

$apps = @(
    "accounts",
    "roles",
    "departments",
    "campuses",
    "warehouses",
    "categories",
    "products",
    "suppliers",
    "purchase_orders",
    "stock_entries",
    "stock_outputs",
    "stock_movements",
    "transfers",
    "requests",
    "inventories",
    "notifications",
    "audit_logs",
    "attachments",
    "maintenance",
    "qr_codes",
    "barcodes",
    "settings",
    "reports",
    "analytics"
)

foreach ($app in $apps) {
    Write-Host "  - $app..." -ForegroundColor Gray
    python manage.py makemigrations $app --noinput 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✓ OK" -ForegroundColor Green
    } else {
        Write-Host "    ⚠ Erreur" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "2. Application des migrations..." -ForegroundColor Yellow
python manage.py migrate

Write-Host ""
Write-Host "3. Initialisation des rôles et permissions..." -ForegroundColor Yellow
python manage.py init_roles

Write-Host ""
Write-Host "✓ Migrations terminées avec succès!" -ForegroundColor Green
Write-Host ""
Write-Host "Pour créer un superuser :" -ForegroundColor Cyan
Write-Host "  python manage.py createsuperuser" -ForegroundColor White
