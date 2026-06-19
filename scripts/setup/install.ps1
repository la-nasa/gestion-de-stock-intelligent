# Script d'installation complet du système
Write-Host "Installation du système IUC Inventory..." -ForegroundColor Cyan

# Vérification des prérequis
 = @('python', 'node', 'npm', 'docker', 'docker-compose')
foreach ( in ) {
    if (Get-Command  -ErrorAction SilentlyContinue) {
        Write-Host "✓  installé" -ForegroundColor Green
    } else {
        Write-Host "✗  non trouvé" -ForegroundColor Red
    }
}

# Installation backend
Write-Host "
Installation du backend..." -ForegroundColor Yellow
cd ../backend
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Installation frontend
Write-Host "
Installation du frontend..." -ForegroundColor Yellow
cd ../frontend
npm install

# Installation ML service
Write-Host "
Installation du service ML..." -ForegroundColor Yellow
cd ../ml-service
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt

Write-Host "
✓ Installation terminée!" -ForegroundColor Green
