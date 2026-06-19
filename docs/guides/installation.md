# Guide d'Installation - IUC Inventory System

## Prérequis

### Matériel Minimum
- **CPU** : 4 cœurs
- **RAM** : 8 Go
- **Disque** : 50 Go SSD
- **OS** : Ubuntu 22.04+ / Windows Server 2019+ / macOS 13+

### Logiciels Requis
- **Docker** 24+ & Docker Compose v2
- **Python** 3.13
- **Node.js** 20 LTS
- **PostgreSQL** 16 (si installation manuelle)
- **Redis** 7 (si installation manuelle)



## Installation Rapide (Docker)

### 1. Cloner le projet
```bash
git clone https://github.com/iuc/inventory-system.git
cd inventory-system
```

### 2. Configuration
```bash
cd docker
cp .env.example .env
# Éditer .env avec vos paramètres
nano .env
```

### 3. Démarrer les services
```bash
docker-compose up -d
```

### 4. Vérifier l'état
```bash
docker-compose ps
# Tous les services doivent être "Up"
```

### 5. Accéder à l'application
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/swagger/ |
| Admin Django | http://localhost:8000/admin/ |
| ML Service | http://localhost:8001/docs |
| Grafana | http://localhost:3001 |
| Prometheus | http://localhost:9090 |
| MinIO | http://localhost:9001 |
| RabbitMQ | http://localhost:15672 |
| Flower | http://localhost:5555 |

### 6. Créer le superuser
```bash
docker exec -it iuc_backend python manage.py createsuperuser
```



## Installation Manuelle

### Backend (Django)

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
cp .env.example .env
# Éditer .env avec vos paramètres

# Migrations
python manage.py migrate
python manage.py init_roles

# Créer le superuser
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Démarrer le serveur
python manage.py runserver
```

### Frontend (Next.js)

```bash
cd frontend

# Installer les dépendances
npm install

# Configurer l'environnement
cp .env.example .env.local

# Démarrer en développement
npm run dev

# Build production
npm run build
npm start
```

### ML Service (FastAPI)

```bash
cd ml-service

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Démarrer le service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```



## Vérification de l'Installation

### Health Check API
```bash
curl http://localhost:8000/health/
# Réponse attendue : {"status": "healthy", ...}
```

### Test de connexion
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@iuc.cm", "password": "votre-mot-de-passe"}'
```



## Dépannage

### Les conteneurs ne démarrent pas
```bash
# Vérifier les logs
docker-compose logs -f [service]

# Problèmes courants :
# - Ports déjà utilisés → modifier dans .env
# - Permissions fichiers → chmod -R 755 .
# - Espace disque → docker system prune -a
```

### Erreur de connexion base de données
```bash
# Vérifier que PostgreSQL est accessible
docker exec -it iuc_postgres psql -U iuc_user -d iuc_inventory

# Vérifier les migrations
docker exec -it iuc_backend python manage.py showmigrations
```

### Problèmes de permissions
```bash
# Réinitialiser les permissions
sudo chown -R $USER:$USER .
chmod -R 755 .
```