# Script d'optimisation et vérification qualité
param(
    [switch]$Lint,
    [switch]$Format,
    [switch]$Security,
    [switch]$All
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IUC Inventory - Optimisation Qualité" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($All -or $Lint) {
    Write-Host "🔍 Linting..." -ForegroundColor Yellow
    
    Write-Host "  Backend (Ruff + MyPy)..." -ForegroundColor Gray
    cd $PSScriptRoot\..\backend
    python -m ruff check . --fix 2>&1 | Select-Object -Last 10
    python -m mypy . --ignore-missing-imports 2>&1 | Select-Object -Last 5
    
    Write-Host "  Frontend (ESLint)..." -ForegroundColor Gray
    cd $PSScriptRoot\..\frontend
    npm run lint 2>&1 | Select-Object -Last 10
    
    Write-Host "  ✓ Linting terminé" -ForegroundColor Green
}

if ($All -or $Format) {
    Write-Host ""
    Write-Host "📝 Formatage..." -ForegroundColor Yellow
    
    Write-Host "  Backend (Black + isort)..." -ForegroundColor Gray
    cd $PSScriptRoot\..\backend
    python -m black . --check --diff 2>&1 | Select-Object -Last 5
    python -m isort . --check-only --diff 2>&1 | Select-Object -Last 5
    
    Write-Host "  Frontend (Prettier)..." -ForegroundColor Gray
    cd $PSScriptRoot\..\frontend
    npx prettier --check "src/**/*.{ts,tsx}" 2>&1 | Select-Object -Last 10
    
    Write-Host "  ✓ Vérification formatage terminée" -ForegroundColor Green
}

if ($All -or $Security) {
    Write-Host ""
    Write-Host "🛡️ Analyse sécurité..." -ForegroundColor Yellow
    
    Write-Host "  Bandit (Python)..." -ForegroundColor Gray
    cd $PSScriptRoot\..\backend
    python -m bandit -r . -c pyproject.toml 2>&1 | Select-Object -Last 15
    
    Write-Host "  ✓ Analyse sécurité terminée" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Optimisation terminée !" -ForegroundColor Green
Write-Host ""
Write-Host "Pour appliquer les corrections automatiques :" -ForegroundColor Cyan
Write-Host "  Formatage:  python -m black . && python -m isort ." -ForegroundColor White
Write-Host "  Linting:    python -m ruff check . --fix" -ForegroundColor White
Write-Host "  Prettier:   npx prettier --write 'src/**/*.{ts,tsx}'" -ForegroundColor White