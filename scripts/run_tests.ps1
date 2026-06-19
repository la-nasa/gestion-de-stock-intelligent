# Script de lancement des tests complets
param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$All,
    [switch]$Coverage
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IUC Inventory - Suite de Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($All -or $Backend) {
    Write-Host "🔧 Tests Backend (Django)..." -ForegroundColor Yellow
    Write-Host ""
    
    cd $PSScriptRoot\..\backend
    
    if ($Coverage) {
        pytest --cov=apps --cov=services --cov=api --cov-report=html --cov-report=term -v
    } else {
        pytest -v
    }
    
    Write-Host ""
    Write-Host "✓ Tests Backend terminés" -ForegroundColor Green
}

if ($All -or $Frontend) {
    Write-Host ""
    Write-Host "🎨 Tests Frontend (Jest)..." -ForegroundColor Yellow
    Write-Host ""
    
    cd $PSScriptRoot\..\frontend
    
    if ($Coverage) {
        npm test -- --coverage
    } else {
        npm test
    }
    
    Write-Host ""
    Write-Host "✓ Tests Frontend terminés" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Tous les tests sont terminés !" -ForegroundColor Green